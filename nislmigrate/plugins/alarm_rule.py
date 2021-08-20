from nislmigrate.migrators.migrator_factory import MigratorFactory
from nislmigrate.service import ServicePlugin


class AlarmRulePlugin(ServicePlugin):

    @property
    def names(self):
        return ["alarmrule", "alarms", "alarm"]

    @property
    def help(self):
        return "Migrate Tag alarm rules"

    def capture(self, migration_directory: str, migrator_factory: MigratorFactory):
        mongo_migrator = migrator_factory.get_mongo_migrator()
        mongo_migrator.capture_migration(self, migration_directory)

    def restore(self, migration_directory: str, migrator_factory: MigratorFactory):
        mongo_migrator = migrator_factory.get_mongo_migrator()
        mongo_migrator.restore_migration(self, migration_directory)

    def restore_error_check(self, migration_directory: str, migrator_factory: MigratorFactory):
        pass
