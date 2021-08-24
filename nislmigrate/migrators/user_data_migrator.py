from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migrator_plugin import MigratorPlugin


class UserDataPlugin(MigratorPlugin):

    @property
    def names(self):
        return ["userdata", "ud"]

    @property
    def help(self):
        return "Migrate user data"

    def capture(self, mongo_handler=None, file_handler=None):
        pass

    def restore(self, mongo_handler=None, file_handler=None):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
