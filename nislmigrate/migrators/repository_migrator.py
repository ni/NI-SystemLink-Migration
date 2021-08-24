import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin


repository_dict = {
    "arg": "repository",
    "name": "Repository",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "Respository",
    "source_dir": os.path.join(
        os.environ.get("ProgramW6432"),
        "National Instruments",
        "Shared",
        "Web Services",
        "NI",
        "repo_webservice",
        "files",
    ),
}


class RepositoryMigrator(MigratorPlugin):

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
