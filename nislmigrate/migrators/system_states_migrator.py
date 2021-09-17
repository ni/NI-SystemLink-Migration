import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from typing import Any, Dict

DEFAULT_GIT_REPOT_PATH = os.path.join(
    str(os.environ.get('ProgramData')),
    'National Instruments',
    'Skyline',
    'Data',
    'SystemsStateManager',
    'States')

GIT_REPO_CONFIG_CONFIGURATION_KEY = 'Git.RepoPath'


class SystemStatesMigrator(MigratorPlugin):

    @property
    def name(self):
        return 'SystemsState'

    @property
    def argument(self):
        return 'systemstates'

    @property
    def help(self):
        return 'Migrate system states'

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
            self.__find_git_repo_directory(facade_factory),
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
            self.__find_git_repo_directory(facade_factory),
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

    def __find_git_repo_directory(self, facade_factory: FacadeFactory) -> str:
        config = self.config(facade_factory)
        return config.get(GIT_REPO_CONFIG_CONFIGURATION_KEY) or DEFAULT_GIT_REPOT_PATH
