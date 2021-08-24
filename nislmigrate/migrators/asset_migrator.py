from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin

asset_dict = {
    "arg": "asset",
    "name": "AssetPerformanceManagement",
    "directory_migration": False,
    "singlefile_migration": False,
}


class AssetMigrator(MigratorPlugin):

    @property
    def argument(self):
        return "assets"

    @property
    def name(self):
        return "AssetPerformanceManagement"

    @property
    def help(self):
        return "Migrate asset utilization and calibration data"

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade = facade_factory.get_mongo_facade()
        mongo_configuration = MongoConfiguration(self.config)
        mongo_facade.capture_mongo_collection_to_directory(mongo_configuration, migration_directory)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade = facade_factory.get_mongo_facade()
        mongo_configuration = MongoConfiguration(self.config)
        mongo_facade.capture_mongo_collection_to_directory(mongo_configuration, migration_directory)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
