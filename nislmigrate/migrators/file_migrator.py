from argparse import ArgumentParser
import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade

DEFAULT_DATA_DIRECTORY = os.path.join(
    str(os.environ.get("ProgramData")),
    "National Instruments",
    "Skyline",
    "Data",
    "FileIngestion")

PATH_CONFIGURATION_KEY = 'OutputPath'


class FileMigrator(MigratorPlugin):

    @property
    def name(self):
        return "FileIngestion"

    @property
    def argument(self):
        return "files"

    @property
    def help(self):
        return "Migrate ingested files"

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
            self.__data_directory(facade_factory),
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
            self.__data_directory(facade_factory),
            True)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)

    def __data_directory(self, facade_factory):
        return self.config(facade_factory).get(PATH_CONFIGURATION_KEY, DEFAULT_DATA_DIRECTORY)

    def add_additional_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('--files-metadata-only',
            help='Capture/restore the file metadata only, not the files themselves. Ignored without --files or --all.',
            action='store_true')


