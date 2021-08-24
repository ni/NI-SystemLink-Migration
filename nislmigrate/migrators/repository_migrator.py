from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migrator_plugin import MigratorPlugin


class RepositoryPlugin(MigratorPlugin):

    @property
    def names(self):
        return ["repository", "repo"]

    @property
    def help(self):
        return "Migrate packages and feeds"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
