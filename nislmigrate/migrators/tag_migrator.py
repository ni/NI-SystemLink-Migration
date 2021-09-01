from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_configuration import MongoConfiguration
import os

from nislmigrate.facades.mongo_facade import MongoFacade


class TagMigrator(MigratorPlugin):

    @property
    def name(self):
        return "TagHistorian"

    @property
    def argument(self):
        return "tags"

    @property
    def help(self):
        return "migrate tags and tag histories"

    __file_to_migrate = "dump.rdb"
    __file_to_migrate_directory = os.path.join(
        str(os.environ.get("ProgramData")),
        "National Instruments",
        "Skyline",
        "KeyValueDatabase")

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_file(
            self.__file_to_migrate_directory,
            migration_directory,
            self.__file_to_migrate)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.copy_file(
            migration_directory,
            self.__file_to_migrate_directory,
            self.__file_to_migrate)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)
