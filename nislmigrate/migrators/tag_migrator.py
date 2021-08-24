from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
import os


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

    __ni_directory = os.path.join(os.environ.get("ProgramData"), "National Instruments")
    __singlefile_dir = os.path.join(__ni_directory, "Skyline", "KeyValueDatabase")
    __singlefile = "dump.rdb"

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade = facade_factory.get_mongo_facade()
        file_facade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config)
        mongo_facade.capture_mongo_collection_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.capture_singlefile(
            migration_directory,
            self.name,
            self.__singlefile_dir,
            self.__singlefile)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade = facade_factory.get_mongo_facade()
        file_facade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config)
        mongo_facade.restore_mongo_collection_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.restore_singlefile(
            migration_directory,
            self.name,
            self.__singlefile_dir,
            self.__singlefile)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        mongo_facade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_mongo_collection_from_directory(migration_directory,
                                                                          self.name)
