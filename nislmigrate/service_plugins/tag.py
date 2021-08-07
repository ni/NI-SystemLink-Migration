from nislmigrate.service import ServicePlugin
import os
import nislmigrate.constants as constants


class TagPlugin(ServicePlugin):

    @property
    def names(self):
        return ["tag", "tags", "tagingestion", "taghistory"]

    @property
    def help(self):
        return "Migrate tags and tag histories"

    _singlefile_dir = os.path.join(constants.program_data_dir, "National Instruments", "Skyline", "KeyValueDatabase")
    _singlefile = "dump.rdb"

    def capture(self, args, mongo_handler=None, file_handler=None):
        mongo_handler.capture_migration(self)
        file_handler.capture_singlefile
        (
            self,
            self._singlefile_dir,
            self._singlefile,
        )

    def restore(self, args, mongo_handler=None, file_handler=None):
        mongo_handler.restore_migration(self)
        file_handler.restore_singlefile
        (
            self,
            self._singlefile_dir,
            self._singlefile,
        )
