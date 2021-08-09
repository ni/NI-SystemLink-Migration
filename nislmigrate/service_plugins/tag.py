from nislmigrate.service import ServicePlugin
import os
import nislmigrate.constants as constants


class TagPlugin(ServicePlugin):

    @property
    def names(self):
        return ["TagHistorian", "taghistory", "tags", "tagingestion", "tag"]

    @property
    def help(self):
        return "Migrate tags and tag histories"

    _singlefile_dir = os.path.join(constants.program_data_dir, "National Instruments", "Skyline", "KeyValueDatabase")
    _singlefile = "dump.rdb"

    def capture(self, migration_directory: str, mongo_handler=None, file_handler=None):
        mongo_handler.capture_migration(self, migration_directory)
        file_handler.capture_singlefile(migration_directory, self, self._singlefile_dir, self._singlefile)

    def restore(self, migration_directory: str, mongo_handler=None, file_handler=None):
        mongo_handler.restore_migration(self, migration_directory)
        file_handler.restore_singlefile(migration_directory, self, self._singlefile_dir, self._singlefile)

    def restore_error_check(self, migration_directory: str, mongo_handler=None, file_handler=None):
        pass