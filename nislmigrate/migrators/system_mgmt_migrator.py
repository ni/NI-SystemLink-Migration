from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
import os
from typing import Any, Dict

PKI_PATH = os.path.join(
    str(os.environ.get('ProgramData')),
    'National Instruments',
    'salt',
    'conf',
    'pki',
    'master')

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
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            PKI_PATH,
            file_migration_directory,
            True)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            PKI_PATH,
            file_migration_directory,
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
