from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migrator_plugin import MigratorPlugin


class FilePlugin(MigratorPlugin):

    @property
    def names(self):
        return ["states", "state", ]

    @property
    def help(self):
        return "Migrate system states"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
