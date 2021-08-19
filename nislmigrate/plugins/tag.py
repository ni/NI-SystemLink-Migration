from nislmigrate.migrators.migrator_factory import MigratorFactory
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

    __ni_directory = os.path.join(constants.program_data_dir, "National Instruments")
    __singlefile_dir = os.path.join(__ni_directory, "Skyline", "KeyValueDatabase")
    __singlefile = "dump.rdb"

    def capture(self, migration_directory: str, migrator_factory: MigratorFactory):
        mongo_migrator = migrator_factory.get_mongo_migrator()
        file_migrator = migrator_factory.get_file_migrator()
        mongo_migrator.capture_migration(self.config, migration_directory)
        file_migrator.capture_singlefile(migration_directory,
                                         self.name,
                                         self.__singlefile_dir,
                                         self.__singlefile)

    def restore(self, migration_directory: str, migrator_factory: MigratorFactory):
        mongo_migrator = migrator_factory.get_mongo_migrator()
        file_migrator = migrator_factory.get_file_migrator()
        mongo_migrator.restore_migration(self.config, migration_directory)
        file_migrator.restore_singlefile(migration_directory,
                                         self.name,
                                         self.__singlefile_dir,
                                         self.__singlefile)

    def restore_error_check(self, migration_directory: str, migrator_factory: MigratorFactory):
        pass
