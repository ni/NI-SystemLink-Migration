from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin

thdbbug_dict = {
    "arg": "thdbbug",
    "name": "TagHistorian",
    "directory_migration": False,
    "singlefile_migration": False,
    "intradb_migration": True,
    "collections_to_migrate": ["metadata", "values"],
    "source_db": "admin",
    "destination_db": "nitaghistorian",
}


class THDBBugMigrator(MigratorPlugin):

    @property
    def argument(self):
        return "thdbbug"

    @property
    def name(self):
        return "TagHistorian"

    @property
    def help(self):
        return "Migrate tag history data to the correct MongoDB to resolve an issue introduced" \
               " in SystemLink 2020R2 when using a remote Mongo instance."

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.migrate_within_instance(mongo_configuration, "admin")

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
