import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade


class RepositoryMigrator(MigratorPlugin):

    @property
    def name(self):
        return "Repository"

    @property
    def argument(self):
        return "repo"

    @property
    def help(self):
        return "Migrate packages and feeds"

    __data_directory = os.path.join(
        str(os.environ.get("ProgramW6432")),
        "National Instruments",
        "Shared",
        "Web Services",
        "NI",
        "repo_webservice",
        "files")

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, "files")

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            self.__data_directory,
            file_migration_directory,
            False)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        file_migration_directory = os.path.join(migration_directory, "files")

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_directory(
            file_migration_directory,
            self.__data_directory,
            True)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)
