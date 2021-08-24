import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin


fis_dict = {
    "arg": "fis",
    "name": "FileIngestion",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "FileIngestion",
    "source_dir": os.path.join(
        os.environ.get("ProgramData"), "National Instruments", "Skyline", "Data", "FileIngestion"
    ),
}


class FileMigrator(MigratorPlugin):

    @property
    def names(self):
        return ["fis", "file", "files"]

    @property
    def help(self):
        return "Migrate ingested files"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
