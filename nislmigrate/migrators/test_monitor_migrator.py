from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin

test_monitor_dict = {
    "arg": "testmonitor",
    "name": "TestMonitor",
    "directory_migration": False,
    "singlefile_migration": False,
}


class TestMonitorMigrator(MigratorPlugin):

    @property
    def argument(self):
        return "tests"

    @property
    def name(self):
        return "testmonitor"

    @property
    def help(self):
        return "Migrate Test Monitor data"

    def capture(self, mongo_handler=None, file_handler=None):
        pass

    def restore(self, mongo_handler=None, file_handler=None):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
