from nislmigrate.migrator_factory import MigratorFactory
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

    def capture(self, migration_directory: str, migrator_factory: MigratorFactory):
        mongo_migrator = migrator_factory.get_mongo_migrator()
        file_migrator = migrator_factory.get_file_migrator()
        mongo_migrator.capture_migration(self, migration_directory)
        file_migrator.capture_singlefile(migration_directory, self, self._singlefile_dir, self._singlefile)

    def restore(self, migration_directory: str, migrator_factory: MigratorFactory):
        mongo_migrator = migrator_factory.get_mongo_migrator()
        file_migrator = migrator_factory.get_file_migrator()
        mongo_migrator.restore_migration(self, migration_directory)
        file_migrator.restore_singlefile(migration_directory, self, self._singlefile_dir, self._singlefile)

    def restore_error_check(self, migration_directory: str, migrator_factory: MigratorFactory):
        pass