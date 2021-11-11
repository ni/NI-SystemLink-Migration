from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.utility.paths import get_ni_application_data_directory_path
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.argument_handler import SECRET_ARGUMENT
import os
from typing import Any, Dict

PKI_DIRECTORY_NAME = 'pki'
PILLAR_DIRECTORY_NAME = 'pillar'
SALT_PATH = os.path.join(get_ni_application_data_directory_path(), 'salt')
PKI_INSTALLED_PATH = os.path.join(SALT_PATH, 'conf', PKI_DIRECTORY_NAME, 'master')
PILLAR_INSTALLED_PATH = os.path.join(SALT_PATH, 'srv', PILLAR_DIRECTORY_NAME)
NO_SECRET_ERROR = """

Migrating systems requires a password to encrypt secrets.
The same password needs to be provided during both capture and restore by
including the following command line argument:

--secret <SECRET>

"""


class SystemsManagementMigrator(MigratorPlugin):

    __file_facade: FileSystemFacade

    @property
    def argument(self):
        return 'systems'

    @property
    def name(self):
        return 'SystemsManagement'

    @property
    def help(self):
        return 'Migrate registered systems. Must include the --secret <SECRET> command line argument when using this ' \
               'migrator. '

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        self.__capture_mongo_data(facade_factory, migration_directory)
        self.__capture_file_data(arguments, migration_directory)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        self.__restore_mongo_data(facade_factory, migration_directory)
        self.__restore_file_data(arguments, facade_factory, migration_directory)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(migration_directory, self.name)
        self.__verify_captured_salt_files_exist(facade_factory, migration_directory)
        self.__verify_secret_provided(arguments)

    def pre_capture_check(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        self.__verify_secret_provided(arguments)

    @staticmethod
    def __verify_secret_provided(arguments):
        secret = arguments.get(SECRET_ARGUMENT)
        if not secret:
            raise MigrationError(NO_SECRET_ERROR)

    def __capture_file_data(self, arguments, migration_directory):
        encrypted_pki_files = os.path.join(migration_directory, PKI_DIRECTORY_NAME)
        encrypted_pillar_files = os.path.join(migration_directory, PILLAR_DIRECTORY_NAME)
        secret = arguments.get(SECRET_ARGUMENT)
        self.__file_facade.copy_directory_to_encrypted_file(PKI_INSTALLED_PATH, encrypted_pki_files, secret)
        if self.__file_facade.does_directory_exist(PILLAR_INSTALLED_PATH):
            self.__file_facade.copy_directory_to_encrypted_file(PILLAR_INSTALLED_PATH, encrypted_pillar_files, secret)

    def __capture_mongo_data(self, facade_factory, migration_directory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.capture_database_to_directory(mongo_configuration, migration_directory, self.name)

    @staticmethod
    def __restore_file_data(arguments, facade_factory, migration_directory):
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        encrypted_pki_files = os.path.join(migration_directory, PKI_DIRECTORY_NAME)
        encrypted_pillar_files = os.path.join(migration_directory, PILLAR_DIRECTORY_NAME)
        secret = arguments.get(SECRET_ARGUMENT)
        file_facade.copy_directory_from_encrypted_file(encrypted_pki_files, PKI_INSTALLED_PATH, secret)
        if file_facade.does_file_exist(encrypted_pillar_files):
            file_facade.copy_directory_from_encrypted_file(encrypted_pillar_files, PILLAR_INSTALLED_PATH, secret)

    def __restore_mongo_data(self, facade_factory, migration_directory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.restore_database_from_directory(mongo_configuration, migration_directory, self.name)

    @staticmethod
    def __verify_captured_salt_files_exist(facade_factory, migration_directory):
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        encrypted_salt_file_path = os.path.join(migration_directory, PKI_DIRECTORY_NAME)
        if not file_facade.does_file_exist(encrypted_salt_file_path):
            raise FileNotFoundError(f"Could not find the captured service at '{encrypted_salt_file_path}'")
