"""Handle Mongo operations."""

import json
import os
import subprocess
import sys
from types import SimpleNamespace

import bson
from pymongo import errors as mongo_errors
from pymongo import MongoClient

from nislmigrate import constants
from nislmigrate.migration_action import MigrationAction


MONGO_MIGRATION_DIRECTORY = "mongo-dump"


class MongoHandler:
    is_mongo_process_running = False
    mongo_process_handle = None

    def get_service_config(self, service):
        """
        Gets the path to the configuration file for the given service.

        :param service: The service name to get the configuration file for.
        :return: The path to a service configuration file.
        """
        config_file = os.path.join(constants.service_config_dir, service.name + ".json")
        with open(config_file, encoding="utf-8-sig") as json_file:
            return json.load(json_file)

    def start_mongo(self):
        """
        Begins the mongo DB subprocess on this computer.

        :return: The started subprocess handling mongo DB.
        """
        if self.is_mongo_process_running:
            return
        self.mongo_process_handle = subprocess.Popen(
            constants.mongod_exe + " --config " + '"' + str(constants.mongo_config) + '"',
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=os.environ,
        )
        self.is_mongo_process_running = True

    def stop_mongo(self):
        """
        Stops the given process.

        :return: None.
        """
        if not self.is_mongo_process_running:
            return
        subprocess.Popen.kill(self.mongo_process_handle)
        self.is_mongo_process_running = False

    def get_connection_args(self, service_config, action: MigrationAction):
        if "Mongo.CustomConnectionString" in service_config:
            args = " --uri {0}".format(service_config["Mongo.CustomConnectionString"])
            if action == MigrationAction.RESTORE:
                # We need to provide the db option (even though it's redundant with the uri) because of a bug with mongoDB 4.2
                # https://docs.mongodb.com/v4.2/reference/program/mongorestore/#cmdoption-mongorestore-uri
                args += " --db {0}".format(service_config["Mongo.Database"])
        else:
            args = " --port {0} --db {1} --username {2} --password {3}".format(
                str(service_config["Mongo.Port"]),
                service_config["Mongo.Database"],
                service_config["Mongo.User"],
                service_config["Mongo.Password"]
            )
        return args

    def capture_migration(self, service, migration_directory: str):
        """
        Capture the data in mongoDB from the given service.

        :param service: The service to capture the data for.
        :param migration_directory: The directory to migrate the service in to.
        :return: None.
        """
        # TODO get rid of the [service.name] by changing the property
        config = self.get_service_config(service)
        connection_arguments = self.get_connection_args(config[service.name], MigrationAction.CAPTURE)
        cmd_to_run = constants.mongo_dump + connection_arguments + " --out " + os.path.join(migration_directory, MONGO_MIGRATION_DIRECTORY) + " --gzip"
        self.ensure_mongo_process_is_running_and_execute_command(cmd_to_run)

    def restore_migration(self, service, migration_directory: str):
        """
        Restore the data in mongoDB from the given service.

        :param service: The service to capture the data for.
        :param migration_directory: The directory to restore the service in to.
        :return: None.
        """
        config = self.get_service_config(service)
        mongo_dump_file = os.path.join(
            migration_directory,
            MONGO_MIGRATION_DIRECTORY,
            config[service.name]["Mongo.Database"])
        connection_arguments = self.get_connection_args(config[service.name], MigrationAction.RESTORE)
        cmd_to_run = constants.mongo_restore + connection_arguments + " --gzip " + mongo_dump_file
        self.ensure_mongo_process_is_running_and_execute_command(cmd_to_run)

    def migrate_document(self, destination_collection, document):
        """
        Inserts a document into a collection.

        :param destination_collection: The collection to migrate the document to.
        :param document: The document to migrate.
        :return: None.
        """
        try:
            print("Migrating " + str(document["_id"]))
            destination_collection.insert_one(document)
        except mongo_errors.DuplicateKeyError:
            print("Document " + str(document["_id"]) + " already exists. Skipping")

    def identify_metadata_conflict(self, destination_collection, source_document):
        """
        Gets any conflicts that would occur if adding source_document to a document collection.

        :param destination_collection: The collection to see if there are conflicts in.
        :param source_document: The document to test if it conflicts.
        :return: The conflicts, if there are any.
        """
        destination_query = {
            "$and": [
                {"workspace": source_document["workspace"]},
                {"path": source_document["path"]},
            ]
        }
        destination_document = destination_collection.find_one(destination_query)
        if destination_document:
            return SimpleNamespace(
                **{
                    "source_id": source_document["_id"],
                    "destination_id": destination_document["_id"],
                }
            )

        return None

    def merge_history_document(self, source_id, destination_id, destination_db):
        """
        Merges the contents of one document into another document.

        :param source_id: The document to merge from.
        :param destination_id: The document to merge in to.
        :param destination_db: The database to merge the history document in.
        :return: None.
        """
        destination_collection = destination_db.get_collection("values")
        destination_collection.update_one(
            {"metadataId": source_id}, {"$set": {"metadataId": destination_id}}
        )

    def migrate_metadata_collection(self, source_db, destination_db):
        """
        Migrates a collection with the name "metadata" from the source database to the destination database.

        :param source_db: The database to migrate from.
        :param destination_db: The database to migrate to.
        :return: None.
        """
        collection_name = "metadata"
        source_collection = source_db.get_collection(collection_name)
        source_collection_iterable = source_collection.find()
        destination_collection = destination_db.get_collection(collection_name)
        for source_document in source_collection_iterable:
            conflict = self.identify_metadata_conflict(destination_collection, source_document)
            if conflict:
                print("Conflict Found! " + "source_id=" + str(conflict.source_id) + " destination_id=" + str(conflict.destination_id))

                self.merge_history_document(conflict.source_id, conflict.destination_id, destination_db)
            else:
                self.migrate_document(destination_collection, source_document)

    def migrate_values_collection(self, source_db, destination_db):
        """
        Migrates a collection with the name "values" from the source database to the destination database.

        :param source_db: The database to migrate from.
        :param destination_db: The database to migrate to.
        :return: None.
        """
        collection_name = "values"
        collection_iterable = source_db.get_collection(collection_name).find()
        destination_collection = destination_db.get_collection(collection_name)
        for document in collection_iterable:
            self.migrate_document(destination_collection, document)

    def check_merge_history_readiness(self, destination_db):
        """
        Checks whether a database is ready for data to be migrated to it.

        :param destination_db: The database to check and see if it is ready for data to be migrated into it.
        :return: None.
        """
        # look for fields that should be set when Org modeling is present. If they are missing exit.
        collection_name = "metadata"
        destination_collection = destination_db.get_collection(collection_name)
        if destination_collection.find({"workspace": {"$exists": False}}).count() > 0:
            print(
                "Database is not ready for migration. Update the connection string in "
                "C:\\ProgramData\\National Instruments\\Skyline\\Config\\TagHistorian.json to "
                "point to the nitaghistorian database in your MongoDB instance and restart Service "
                "Manager. Please see <TODO: DOCUMENTATION LINK HERE> for more detail"
            )
            sys.exit()

    # TODO: Get rid of 'config' parameter if it is not used.
    def migrate_within_instance(self, service, action, config):
        """
        Migrates the data for a service from one mongo database to another mongo database.

        :param service: The service to migrate.
        :param action: Whether to capture or restore.
        :param config: Any additional configuration that might be needed to complete the migration.
        :return: None.
        """
        codec = bson.codec_options.CodecOptions(uuid_representation=bson.binary.UUID_SUBTYPE)
        config = self.get_service_config(constants.no_sql)
        client = MongoClient(
            host=[config[constants.no_sql.name]["Mongo.Host"]],
            port=config[constants.no_sql.name]["Mongo.Port"],
            username=config[constants.no_sql.name]["Mongo.User"],
            password=config[constants.no_sql.name]["Mongo.Password"],
        )
        source_db = client.get_database(name=service.SOURCE_DB, codec_options=codec)
        destination_db = client.get_database(name=service.destination_db, codec_options=codec)
        self.check_merge_history_readiness(destination_db)
        self.migrate_values_collection(source_db, destination_db)
        self.migrate_metadata_collection(source_db, destination_db)

    def migrate_mongo_cmd(self, service, action: MigrationAction, config, migration_directory: str):
        """
        Performs a restore or a capture operation depending on the chosen action.

        :param service: The service to capture or restore.
        :param action: Whether to capture or restore.
        :param config: The mongo configuration for the service to migrate.
        :param migration_directory: Directory to capture into or capture from.
        :return: None.
        """
        if action == constants.thdbbug.arg:
            self.migrate_within_instance(service, action, config)
        if action == MigrationAction.CAPTURE:
            self.capture_migration(service, action, config, migration_directory)
        if action == MigrationAction.RESTORE:
            self.restore_migration(service, action, config, migration_directory)

    def ensure_mongo_process_is_running_and_execute_command(self, command: str):
        self.start_mongo()
        subprocess.run(command, check=True)
