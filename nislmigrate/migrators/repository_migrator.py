import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.utility.paths import get_ni_shared_directory_64_path
from typing import Any, Dict

BASE_REPOSITORY_PATH_CONFIG_TOKEN = 'BaseFilePath'
DEFAULT_BASE_REPOSITORY_PATH = os.path.join(
    get_ni_shared_directory_64_path(),
    'Web Services',
    'NI',
    'repo_webservice',
    'files')


class RepositoryMigrator(MigratorPlugin):

    @property
    def name(self):
        return 'PackageRepository'

    @property
    def argument(self):
        return 'repo'

    @property
    def help(self):
        return 'Migrate packages and feeds'

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory_if_exists(
            self.__find_repository_path(facade_factory),
            file_migration_directory,
            False)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, 'files')

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory_if_exists(
            file_migration_directory,
            self.__find_repository_path(facade_factory),
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

    def __find_repository_path(self, facade_factory: FacadeFactory) -> str:
        config = self.config(facade_factory)
        return config.get(BASE_REPOSITORY_PATH_CONFIG_TOKEN) or DEFAULT_BASE_REPOSITORY_PATH
