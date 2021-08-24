import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin


states_dict = {
    "arg": "states",
    "name": "SystemsStateManager",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "SystemsStateManager",
    "source_dir": os.path.join(
        os.environ.get("ProgramData"),
        "National Instruments",
        "Skyline",
        "Data",
        "SystemsStateManager",
    ),
}


class StatesMigrator(MigratorPlugin):

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
