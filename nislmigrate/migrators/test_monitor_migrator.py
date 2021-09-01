from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade


class TestMonitorMigrator(MigratorPlugin):

    @property
    def name(self):
        return "TestMonitor"

    @property
    def argument(self):
        return "testmonitor"

    @property
    def help(self):
        return "Migrate notifications strategies, templates, and groups"

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(
            migration_directory,
            self.name)
