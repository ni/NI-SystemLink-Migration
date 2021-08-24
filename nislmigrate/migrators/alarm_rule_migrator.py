from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin


alarm_rule_dict = {
    "arg": "alarmrule",
    "name": "TagRuleEngine",
    "directory_migration": False,
    "singlefile_migration": False,
}


class AlarmRuleMigrator(MigratorPlugin):

    @property
    def names(self):
        return ["alarmrule", "alarms", "alarm"]

    @property
    def help(self):
        return "Migrate Tag alarm rules"

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration = MongoConfiguration(self.config)
        mongo_facade.capture_mongo_collection_to_directory(
            mongo_configuration,
            migration_directory)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration = MongoConfiguration(self.config)
        mongo_facade.restore_mongo_collection_from_directory(
            mongo_configuration,
            migration_directory)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration = MongoConfiguration(self.config)
        mongo_facade.validate_can_restore_mongo_collection_from_directory(
            mongo_configuration,
            migration_directory)
