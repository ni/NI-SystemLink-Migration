from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from typing import Any, Dict

thdbbug_dict = {
    'arg': 'thdbbug',
    'name': 'TagHistorian',
    'directory_migration': False,
    'singlefile_migration': False,
    'intradb_migration': True,
    'collections_to_migrate': ['metadata', 'values'],
    'source_db': 'admin',
    'destination_db': 'nitaghistorian',
}


# The TagHistorianDatabase bug migrator is intended to fix the database bug introduced in SystemLink 2020R1.
# This class does not currently extend MigratorPlugin so it is not discovered as a plugin and can not be used.
# As part of F1247651, this is the code that will fix the DB bug, we just need to expose it to the user in
# a reasonable way.
class THDBBugMigrator:

    @property
    def argument(self):
        return 'thdbbug'

    @property
    def name(self):
        return 'TagHistorian'

    @property
    def help(self):
        return 'Migrate tag history data to the correct MongoDB to resolve an issue introduced' \
               ' in SystemLink 2020R2 when using a remote Mongo instance.'

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration({})
        mongo_facade.migrate_within_instance(mongo_configuration, 'admin')

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        pass

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        pass
