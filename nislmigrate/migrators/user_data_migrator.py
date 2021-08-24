from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin


userdata_dict = {
    "arg": "userdata",
    "name": "UserData",
    "directory_migration": False,
    "singlefile_migration": False,
}


class UserDataMigrator(MigratorPlugin):

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
