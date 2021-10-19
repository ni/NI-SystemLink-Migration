from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
import os
from typing import Any, Dict

PKI_RELATIVE_PATH = os.path.join(
    'National Instruments',
    'salt',
    'conf',
    'pki',
    'master')

PKI_INSTALLED_PATH = os.path.join(
    str(os.environ.get('ProgramData')),
    PKI_RELATIVE_PATH)

PILLAR_RELATIVE_PATH = os.path.join(
    'National Instruments',
    'salt',
    'srv',
    'pillar')

PILLAR_INSTALLED_PATH = os.path.join(
    str(os.environ.get('ProgramData')),
    PILLAR_RELATIVE_PATH)


class SystemsManagementMigrator(MigratorPlugin):

    @property
    def argument(self):
        return 'systems'

    @property
    def name(self):
        return 'SystemsManagement'

    @property
    def help(self):
        return 'Migrate registered systems'

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        pki_files_migration_directory = self.__get_pki_files_migration_directory(migration_directory)
        pillar_files_migration_directory = self.__get_pillar_files_migration_directory(migration_directory)

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            PKI_INSTALLED_PATH,
            pki_files_migration_directory,
            True)
        file_facade.copy_directory_if_exists(
            PILLAR_INSTALLED_PATH,
            pillar_files_migration_directory,
            True)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        pki_files_migration_directory = self.__get_pki_files_migration_directory(migration_directory)
        pillar_files_migration_directory = self.__get_pillar_files_migration_directory(migration_directory)

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            pki_files_migration_directory,
            PKI_INSTALLED_PATH,
            True)
        file_facade.copy_directory_if_exists(
            pillar_files_migration_directory,
            PILLAR_INSTALLED_PATH,
            True)

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)

        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        pki_files_migration_directory = self.__get_pki_files_migration_directory(migration_directory)
        if not file_facade.does_directory_exist(pki_files_migration_directory):
            raise FileNotFoundError(f"Could not find the captured service at '{pki_files_migration_directory}'")

    @staticmethod
    def __get_pki_files_migration_directory(migration_directory: str) -> str:
        return os.path.join(migration_directory, PKI_RELATIVE_PATH)

    @staticmethod
    def __get_pillar_files_migration_directory(migration_directory: str) -> str:
        return os.path.join(migration_directory, PILLAR_RELATIVE_PATH)
