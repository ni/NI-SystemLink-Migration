"""Handle Mongo operations."""

import os
import subprocess
import sys
from typing import List, Dict

from bson.codec_options import CodecOptions
from bson.binary import UUID_SUBTYPE
from pymongo import errors as mongo_errors
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from nislmigrate.facades.mongo_configuration import MongoConfiguration

MONGO_CONFIGURATION_PATH: str = os.path.join(os.environ.get("ProgramData"),
                                             "National Instruments",
                                             "Skyline",
                                             "NoSqlDatabase",
                                             "mongodb.conf")
MONGO_BINARIES_DIRECTORY: str = os.path.join(os.environ.get("ProgramW6432"),
                                             "National Instruments",
                                             "Shared",
                                             "Skyline",
                                             "NoSqlDatabase",
                                             "bin")
MONGO_DUMP_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, "mongodump.exe")
MONGO_RESTORE_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, "mongorestore.exe")
MONGO_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, "mongod.exe")


class MongoFacade:
    is_mongo_process_running: bool = False
    mongo_process_handle: subprocess.Popen = None

    def __del__(self):
        self.__stop_mongo()

    def __start_mongo(self) -> None:
        """
        Begins the mongo DB subprocess on this computer.
        :return: The started subprocess handling mongo DB.
        """
        if self.is_mongo_process_running:
            return
        arguments = [MONGO_EXECUTABLE_PATH, "--config", MONGO_CONFIGURATION_PATH]
        self.mongo_process_handle = subprocess.Popen(arguments,
                                                     creationflags=subprocess.CREATE_NEW_CONSOLE,
                                                     env=os.environ)
        self.is_mongo_process_running = True

    def __stop_mongo(self) -> None:
        """
        Stops the mongo process.
        :return: None.
        """
        if self.is_mongo_process_running:
            subprocess.Popen.kill(self.mongo_process_handle)
            self.is_mongo_process_running = False

    @staticmethod
    def __get_mongo_connection_arguments(mongo_configuration: MongoConfiguration) -> List[str]:
        if mongo_configuration.connection_string:
            return ["--uri", mongo_configuration.connection_string]
        return ["--port",
                str(mongo_configuration.port),
                "--db",
                mongo_configuration.collection_name,
                "--username",
                mongo_configuration.user,
                "--password",
                mongo_configuration.password]

    def capture_mongo_collection_to_directory(
            self,
            configuration: MongoConfiguration,
            directory: str,
            dump_name: str) -> None:
        """
        Capture the data in mongoDB from the given service.
        :param configuration: The mongo configuration for a service.
        :param directory: The directory to migrate the service in to.
        :param dump_name: The name of the file to dump to.
        """
        dump_path = os.path.join(directory, dump_name)
        mongo_dump_command = [MONGO_DUMP_EXECUTABLE_PATH]
        connection_arguments = self.__get_mongo_connection_arguments(configuration)
        mongo_dump_command.extend(connection_arguments)
        mongo_dump_command.append("--archive=" + dump_path)
        mongo_dump_command.append("--gzip")
        self.__ensure_mongo_process_is_running_and_execute_command(mongo_dump_command)

    def restore_mongo_collection_from_directory(
            self,
            configuration: MongoConfiguration,
            directory: str,
            dump_name: str) -> None:
        """
        Restore the data in mongoDB from the given service.

        :param configuration: The mongo configuration for a service.
        :param directory: The directory to restore the service from.
        :param dump_name: The name of the file to restore from.
        """
        dump_path = os.path.join(directory, dump_name)
        self.validate_can_restore_mongo_collection_from_directory(directory, dump_name)
        mongo_restore_command = [MONGO_RESTORE_EXECUTABLE_PATH]
        connection_arguments = self.__get_mongo_connection_arguments(configuration)
        # We need to provide the db option (even though it's redundant with the uri)
        # because of a bug with mongoDB 4.2
        # https://docs.mongodb.com/v4.2/reference/program/mongorestore/#cmdoption-mongorestore-uri
        connection_arguments.extend(["--db", configuration.collection_name])
        mongo_restore_command.extend(connection_arguments)
        mongo_restore_command.append("--gzip")
        mongo_restore_command.append("--archive=" + dump_path)
        self.__ensure_mongo_process_is_running_and_execute_command(mongo_restore_command)

    @staticmethod
    def validate_can_restore_mongo_collection_from_directory(
            directory: str,
            dump_name: str,
    ) -> None:
        """
        Throws an exception is restore from the given service is predicted to fail.

        :param configuration: The mongo configuration for a service.
        :param directory: The directory to test restore the service from.
        :param dump_name: The name of the dump that resides in the directory
        `                 to test restoring the service from.
        """
        dump_path = os.path.join(directory, dump_name)
        if not os.path.exists(dump_path):
            raise FileNotFoundError("Could not find the captured service at " + dump_path)

    @staticmethod
    def migrate_document(
            destination_collection: Collection,
            document: Dict[str, any],
    ) -> None:
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

    @staticmethod
    def get_conflicting_document(
            collection: Collection,
            document: Dict[str, any],
    ) -> Dict[str, any]:
        """
        Gets any conflicts that would occur if adding document to a collection.

        :param collection: The collection to see if there are conflicts in.
        :param document: The document to test if it conflicts.
        :return: The document that would conflict, or none if no document conflicts.
        """
        workspace_field = {"workspace": document["workspace"]}
        path_field = {"path": document["path"]}
        query_parameters = [workspace_field, path_field]
        conflict_search_query = {"$and": query_parameters}
        return collection.find_one(conflict_search_query)

    @staticmethod
    def merge_history_document(
            source_id,
            destination_id,
            destination_db,
    ) -> None:
        """
        Merges the contents of one document into another document.

        :param source_id: The document to merge from.
        :param destination_id: The document to merge in to.
        :param destination_db: The database to merge the history document in.
        :return: None.
        """
        destination_collection: Collection = destination_db.get_collection("values")
        destination_collection.update_one(
            {"metadataId": source_id}, {"$set": {"metadataId": destination_id}}
        )

    def migrate_metadata_collection(
            self,
            source_db: Database,
            destination_db: Database,
    ) -> None:
        """
        Migrates a collection with the name "metadata" from the source database
        to the destination database.

        :param source_db: The database to migrate from.
        :param destination_db: The database to migrate to.
        :return: None.
        """
        collection_name = "metadata"
        source_collection = source_db.get_collection(collection_name)
        source_collection_iterable = source_collection.find()
        destination_collection = destination_db.get_collection(collection_name)
        for source_document in source_collection_iterable:
            conflicting_document = self.get_conflicting_document(destination_collection, source_document)
            if conflicting_document:
                source_id = source_document["_id"]
                destination_id = conflicting_document["_id"]
                self.merge_history_document(source_id, destination_id, destination_db)
            else:
                self.migrate_document(destination_collection, source_document)

    def migrate_values_collection(
            self,
            source_db: Database,
            destination_db: Database) -> None:
        """
        Migrates a collection with the name "values" from the source database
        to the destination database.

        :param source_db: The database to migrate from.
        :param destination_db: The database to migrate to.
        :return: None.
        """
        collection_name = "values"
        collection_iterable = source_db.get_collection(collection_name).find()
        destination_collection = destination_db.get_collection(collection_name)
        for document in collection_iterable:
            self.migrate_document(destination_collection, document)

    @staticmethod
    def check_merge_history_readiness(destination_db: Database) -> None:
        """
        Checks whether a database is ready for data to be migrated to it.
        :param destination_db: The database to check and see if it is ready
                               for data to be migrated into it.
        """
        # look for fields that should be set when Org modeling is present.
        # If they are missing exit.
        collection_name = "metadata"
        destination_collection = destination_db.get_collection(collection_name)
        if destination_collection.find({"workspace": {"$exists": False}}).count() > 0:
            print(
                "Database is not ready for migration. Update the connection string in "
                "C:\\ProgramData\\National Instruments\\Skyline\\Config\\TagHistorian.json to "
                "point to the nitaghistorian database in your MongoDB instance and restart Service"
                " Manager. Please see <TODO: DOCUMENTATION LINK HERE> for more detail"
            )
            sys.exit()

    def migrate_within_instance(
            self,
            configuration: MongoConfiguration,
            destination_collection_name: str,
    ) -> None:
        """
        Migrates the data for a service from one mongo database to another mongo database.

        :param configuration: The mongo db configuration containing connection information and
                            the name of the source collection.
        :param destination_collection_name: The name of the mongo db collection to migrate to.
        """
        codec = CodecOptions(uuid_representation=UUID_SUBTYPE)
        client = MongoClient(
            host=configuration.host_name,
            port=configuration.port,
            username=configuration.user,
            password=configuration.password,
        )
        source_db: Database = client.get_database(name=configuration.collection_name, codec_options=codec)
        destination_db: Database = client.get_database(name=destination_collection_name, codec_options=codec)
        self.check_merge_history_readiness(destination_db)
        self.migrate_values_collection(source_db, destination_db)
        self.migrate_metadata_collection(source_db, destination_db)

    def __ensure_mongo_process_is_running_and_execute_command(
            self,
            arguments: List[str],
    ) -> None:
        """
        Ensures the mongo service is running and executed the given command in a subprocess.

        :param arguments: The list of arguments to execute in a subprocess.
        """
        try:
            self.__start_mongo()
            subprocess.run(arguments, check=True)
        except subprocess.CalledProcessError as e:
            print(e.stderr)
