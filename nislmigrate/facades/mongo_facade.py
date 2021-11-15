"""Handle Mongo operations."""

import os
import logging
from typing import List, Optional, Callable, Any

import bson
from pymongo import MongoClient

from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.process_facade import ProcessFacade, BackgroundProcess, ProcessError
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.utility.paths import get_ni_application_data_directory_path, get_ni_shared_directory_64_path

MONGO_CONFIGURATION_PATH: str = os.path.join(
    get_ni_application_data_directory_path(),
    'Skyline',
    'NoSqlDatabase',
    'mongodb.conf')
MONGO_BINARIES_DIRECTORY: str = os.path.join(
    get_ni_shared_directory_64_path(),
    'Skyline',
    'NoSqlDatabase',
    'bin')
MONGO_DUMP_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, 'mongodump.exe')
MONGO_RESTORE_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, 'mongorestore.exe')
MONGO_EXECUTABLE_PATH: str = os.path.join(MONGO_BINARIES_DIRECTORY, 'mongod.exe')


class MongoFacade:
    __mongo_process_handle: Optional[BackgroundProcess] = None

    def __init__(self, process_facade: ProcessFacade):
        self.process_facade: ProcessFacade = process_facade

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
            os.makedirs(directory)
        dump_path = os.path.join(directory, dump_name)
        mongo_dump_command = [MONGO_DUMP_EXECUTABLE_PATH]
        connection_arguments = self.__get_mongo_connection_arguments(configuration)
        mongo_dump_command.extend(connection_arguments)
        mongo_dump_command.append('--archive=' + dump_path)
        mongo_dump_command.append('--gzip')
        output = self.__ensure_mongo_process_is_running_and_execute_command(mongo_dump_command)
        self.__check_mongo_output_for_errors(output)

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
        connection_arguments.extend(['--db', configuration.database_name])
        mongo_restore_command.extend(connection_arguments)
        mongo_restore_command.append('--gzip')
        mongo_restore_command.append('--archive=' + dump_path)
        mongo_restore_command.append('--drop')
        output = self.__ensure_mongo_process_is_running_and_execute_command(mongo_restore_command)
        self.__check_mongo_output_for_errors(output)

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
            raise FileNotFoundError('Could not find the captured service at ' + dump_path)

    def __ensure_mongo_process_is_running_and_execute_command(self, arguments: List[str]) -> str:
        """
        Ensures the mongo service is running and executed the given command in a subprocess.

        :param arguments: The list of arguments to execute in a subprocess.
        """

        self.__start_mongo()
        try:
            return self.process_facade.run_process(arguments)
        except ProcessError as e:
            log = logging.getLogger(MongoFacade.__name__)
            log.error(e.error)
        return ''

    def __start_mongo(self) -> None:
        """
        Begins the mongo DB subprocess on this computer.
        :return: The started subprocess handling mongo DB.
        """
        if not self.__mongo_process_handle:
            arguments = [MONGO_EXECUTABLE_PATH, '--config', MONGO_CONFIGURATION_PATH]
            self.__mongo_process_handle = self.process_facade.run_background_process(arguments)

    def __stop_mongo(self) -> None:
        """
        Stops the mongo process.
        :return: None.
        """
        if self.__mongo_process_handle:
            actual_handle: BackgroundProcess = self.__mongo_process_handle
            self.__mongo_process_handle = None
            actual_handle.stop()

    @staticmethod
    def __get_mongo_connection_arguments(mongo_configuration: MongoConfiguration) -> List[str]:
        if mongo_configuration.connection_string:
            return ['--uri', mongo_configuration.connection_string]
        return ['--port',
                str(mongo_configuration.port),
                '--db',
                mongo_configuration.database_name,
                '--username',
                mongo_configuration.user,
                '--password',
                mongo_configuration.password]

    @staticmethod
    def __check_mongo_output_for_errors(output: str):
        if not output:
            return
        raw_lines = output.splitlines()
        lines = [line.split('\t')[1] for line in raw_lines if len(line.split('\t')) > 1]
        for line in lines:
            if 'error:' in line:
                raise MigrationError(f'Mongo reported the following error: {line}')
            else:
                log = logging.getLogger('MongoProcess')
                log.info(f'{line}')

    def update_documents_in_collection(
            self,
            configuration: MongoConfiguration,
            collection_name: str,
            predicate: Callable[[Any], bool],
            update_function: Callable[[Any], Any]):
        client = MongoClient(configuration.connection_string)
        codec = bson.codec_options.CodecOptions(uuid_representation=bson.binary.UUID_SUBTYPE)
        database = client.get_database(name=configuration.database_name, codec_options=codec)
        collection = database[collection_name]
        for document in collection.find():
            if predicate(document):
                document = update_function(document)
                collection.replace_one({'_id': document['_id']}, document)
