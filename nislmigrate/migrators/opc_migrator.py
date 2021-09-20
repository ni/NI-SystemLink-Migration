import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.utility.paths import get_ni_application_data_directory_path
from typing import Any, Dict


class OPCMigrator(MigratorPlugin):

    @property
    def name(self):
        return 'OpcClient'

    @property
    def argument(self):
        return 'opc'

    @property
    def help(self):
        return 'Migrate OPCUA sessions and certificates'

    __ni_directory = get_ni_application_data_directory_path()
    __data_directory = os.path.join(__ni_directory, 'Skyline', 'Data', 'OpcClient')

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade = facade_factory.get_mongo_facade()
        file_facade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            self.__data_directory,
            file_migration_directory,
            False)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade = facade_factory.get_mongo_facade()
        file_facade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            file_migration_directory,
            self.__data_directory,
            True)

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        mongo_facade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)
