"""Handle Mongo operations."""

from nislmigrate.logs.migration_error import MigrationError
import os
import subprocess
import logging
from typing import Callable, List, Dict, Optional, Any

from bson.codec_options import CodecOptions
from bson.binary import UUID_SUBTYPE
from pymongo import errors as mongo_errors
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from nislmigrate.facades.mongo_configuration import MongoConfiguration

MONGO_CONFIGURATION_PATH: str = os.path.join(
    str(os.environ.get("ProgramData")),
    "National Instruments",
    "Skyline",
    "NoSqlDatabase",
    "mongodb.conf")
MONGO_BINARIES_DIRECTORY: str = os.path.join(
    str(os.environ.get("ProgramW6432")),
    "National Instruments",
    "Shared",
    "Skyline",
    "NoSqlDatabase",
    "bin")
MONGO_DUMP_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, "mongodump.exe")
MONGO_RESTORE_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, "mongorestore.exe")
MONGO_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, "mongod.exe")


class MongoFacade:
    mongo_process_handle: Optional[subprocess.Popen] = None

    def capture_database_to_directory(
            self,
            configuration: MongoConfiguration,
            directory: str,
            dump_name: str,
            ) -> None:
        """
        Capture the data in mongoDB from the given service.
        :param configuration: The mongo configuration for a service.
        :param directory: The directory to migrate the service in to.
        :param dump_name: The name of the file to dump to.
        """
        if not os.path.exists(directory):
            os.mkdir(directory)
        dump_path = os.path.join(directory, dump_name)
        mongo_dump_command = [MONGO_DUMP_EXECUTABLE_PATH]
        connection_arguments = self.__get_mongo_connection_arguments(configuration)
        mongo_dump_command.extend(connection_arguments)
        mongo_dump_command.append("--archive=" + dump_path)
        mongo_dump_command.append("--gzip")
        self.__ensure_mongo_process_is_running_and_execute_command(mongo_dump_command)

    def restore_database_from_directory(
            self,
            configuration: MongoConfiguration,
            directory: str,
            dump_name: str,
    ) -> None:
        """
        Restore the data in mongoDB from the given service.

        :param configuration: The mongo configuration for a service.
        :param directory: The directory to restore the service from.
        :param dump_name: The name of the file to restore from.
        """
        dump_path = os.path.join(directory, dump_name)
        self.validate_can_restore_database_from_directory(directory, dump_name)
        mongo_restore_command = [MONGO_RESTORE_EXECUTABLE_PATH]
        connection_arguments = self.__get_mongo_connection_arguments(configuration)
        # We need to provide the db option (even though it's redundant with the uri)
        # because of a bug with mongoDB 4.2
        # https://docs.mongodb.com/v4.2/reference/program/mongorestore/#cmdoption-mongorestore-uri
        connection_arguments.extend(["--db", configuration.database_name])
        mongo_restore_command.extend(connection_arguments)
        mongo_restore_command.append("--gzip")
        mongo_restore_command.append("--archive=" + dump_path)
        self.__ensure_mongo_process_is_running_and_execute_command(mongo_restore_command)

    @staticmethod
    def validate_can_restore_database_from_directory(
            directory: str,
            dump_name: str,
    ) -> None:
        """
        Throws an exception is restore from the given service is predicted to fail.

        :param directory: The directory to test restore the service from.
        :param dump_name: The name of the dump that resides in the directory
        `                 to test restoring the service from.
        """
        dump_path = os.path.join(directory, dump_name)
        if not os.path.exists(dump_path):
            raise FileNotFoundError("Could not find the captured service at " + dump_path)

    @staticmethod
    def migrate_document(collection: Collection, document: Dict[str, Any]) -> None:
        """
        Inserts a document into a collection.

        :param collection: The collection to insert the document in to.
        :param document: The document to insert.
        """
        log = logging.getLogger(MongoFacade.__name__)
        document_id = str(document["_id"])
        try:
            log.log(logging.INFO, "Migrating " + document_id)
            collection.insert_one(document)
        except mongo_errors.DuplicateKeyError:
            log.warning("Document " + document_id + " already exists. Skipping")

    @staticmethod
    def __get_conflicting_document_id(
            collection: Collection,
            document: Dict[str, Any],
    ) -> str:
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
        return collection.find_one(conflict_search_query)["_id"]

    @staticmethod
    def __merge_history_document(
            source_id: str,
            destination_id: str,
            destination_database: Database,
    ) -> None:
        """
        Merges the contents of one document into another document.

        :param source_id: The document to merge from.
        :param destination_id: The document to merge in to.
        :param destination_database: The database to merge the history document in.
        :return: None.
        """
        destination_collection: Collection = destination_database.get_collection("values")
        destination_collection.update_one(
            {"metadataId": source_id}, {"$set": {"metadataId": destination_id}}
        )

    def __migrate_collection(
            self,
            name: str,
            source_database: Database,
            destination_database: Database,
            on_conflict: Optional[Callable[[str, str, Database], None]],
    ) -> None:
        """
        Migrates a collection with the name "values" from the source database
        to the destination database.

        :param name: the name of the collection to migrate from the source database.
        :param source_database: The database to migrate from.
        :param destination_database: The database to migrate to.
        """
        source: Collection = source_database.get_collection(name)
        destination: Collection = destination_database.get_collection(name)
        for document in source:
            if on_conflict:
                conflict_id: str = self.__get_conflicting_document_id(destination, document)
                if conflict_id:
                    source_id = document["_id"]
                    on_conflict(source_id, conflict_id, destination_database)
                    continue
            self.migrate_document(destination, document)

    @staticmethod
    def check_merge_history_readiness(destination_db: Database) -> None:
        """
        Checks whether a database is ready for data to be migrated to it.
        :param destination_db: The database to check and see if it is ready
                               for data to be migrated into it.
        """
        # look for fields that should be set when Org modeling is present.
        collection_name: str = "metadata"
        destination_collection: Collection = destination_db.get_collection(collection_name)
        if destination_collection.find({"workspace": {"$exists": False}}):
            raise MigrationError(
                "Database is not ready for migration. Update the connection string in "
                "C:\\ProgramData\\National Instruments\\Skyline\\Config\\TagHistorian.json to "
                "point to the nitaghistorian database in your MongoDB instance and restart Service"
                " Manager. Please see <TODO: DOCUMENTATION LINK HERE> for more detail"
            )

    def migrate_within_instance(
            self,
            configuration: MongoConfiguration,
            source_database_name: str,
    ) -> None:
        """
        Migrates the data for a service from one mongo database to another mongo database.

        :param configuration: The mongo db configuration containing connection information and
                              the name of the destination collection.
        :param source_database_name: The name of the mongo db collection to migrate to.
        """
        codec: CodecOptions = CodecOptions(uuid_representation=UUID_SUBTYPE)
        client: MongoClient = MongoClient(
            host=configuration.host_name,
            port=configuration.port,
            username=configuration.user,
            password=configuration.password)
        source_database: Database = client.get_database(
            name=source_database_name,
            codec_options=codec)
        destination_database: Database = client.get_database(
            name=configuration.database_name,
            codec_options=codec)
        self.check_merge_history_readiness(destination_database)
        self.__migrate_collection(
            "values",
            source_database,
            destination_database,
            None)
        self.__migrate_collection(
            "metadata",
            source_database,
            destination_database,
            self.__merge_history_document)

    def __ensure_mongo_process_is_running_and_execute_command(self, arguments: List[str]) -> None:
        """
        Ensures the mongo service is running and executed the given command in a subprocess.

        :param arguments: The list of arguments to execute in a subprocess.
        """
        try:
            self.__start_mongo()
            subprocess.run(arguments, check=True)
        except subprocess.CalledProcessError as e:
            log = logging.getLogger(MongoFacade.__name__)
            log.error(e.stderr)

    def __start_mongo(self) -> None:
        """
        Begins the mongo DB subprocess on this computer.
        :return: The started subprocess handling mongo DB.
        """
        if not self.mongo_process_handle:
            arguments = [MONGO_EXECUTABLE_PATH, "--config", MONGO_CONFIGURATION_PATH]
            self.mongo_process_handle = subprocess.Popen(
                arguments,
                env=os.environ,
                creationflags=subprocess.CREATE_NEW_CONSOLE)

    def __del__(self):
        self.__stop_mongo()

    def __stop_mongo(self) -> None:
        """
        Stops the mongo process.
        :return: None.
        """
        if self.mongo_process_handle:
            actual_handle: subprocess.Popen = self.mongo_process_handle
            subprocess.Popen.kill(actual_handle)
            self.mongo_process_handle = None

    @staticmethod
    def __get_mongo_connection_arguments(mongo_configuration: MongoConfiguration) -> List[str]:
        if mongo_configuration.connection_string:
            return ["--uri", mongo_configuration.connection_string]
        return ["--port",
                str(mongo_configuration.port),
                "--db",
                mongo_configuration.database_name,
                "--username",
                mongo_configuration.user,
                "--password",
                mongo_configuration.password]
