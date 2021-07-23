from slmigrate.service import ServicePlugin
import os
import slmigrate.constants as constants


class TagPlugin(ServicePlugin):

    @property
    def names(self):
        return ["tag", "tags", "tagingestion", "taghistory"]

    @property
    def help(self):
        return "Migrate tags and tag histories"

    _singlefile_dir = os.path.join(constants.program_data_dir, "National Instruments", "Skyline", "KeyValueDatabase")
    _singlefile = "dump.rdb"

    def capture(self, args, mongohandler=None, filehandler=None):
        mongohandler.capture_migration(self)
        filehandler.capture_singlefile
        (
            self,
            self._singlefile_dir,
            self._singlefile,
        )

    def restore(self, args, mongohandler=None, filehandler=None):
        mongohandler.restore_migration(self)
        filehandler.restore_singlefile
        (
            self,
            self._singlefile_dir,
            self._singlefile,
        )
