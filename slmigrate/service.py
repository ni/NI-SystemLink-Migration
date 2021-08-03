import slmigrate.constants as constants
import os
import json

from abc import ABC, abstractmethod

class ServicePlugin(ABC):

    cached_config = None

    @property
    @abstractmethod
    def names(self):
        return ["service"]

    @property
    def name(self):
        # first element of the names list is the default name for argparsing
        return self.names[0]

    @property
    @abstractmethod
    def help(self):
        return "A short sentence describing the operation of the plugin"

    @property
    def config(self):
        if self.cached_config is None:
            # most (all?) services use this style of config file.  Plugins won't need to override this method.
            config_file = os.path.join(constants.service_config_dir, self.name + ".json")
            with open(config_file, encoding="utf-8-sig") as json_file:
                self.cached_config = json.load(json_file)
        return self.cached_config;

    @abstractmethod
    def capture(self, mongohandler=None, filehandler=None):
        pass

    @abstractmethod
    def restore(self, mongohandler=None, filehandler=None):
        pass

    def restore_error_check(self, migration_directory: str, mongohandler=None, filehandler=None):
        """TODO: Complete documentation.

        :param service:
        :return:
        """
        if filehandler == None:
            return
        if not filehandler.migration_dir_exists(migration_directory):
            raise FileNotFoundError(migration_directory + " does not exist")
        if not filehandler.service_restore_singlefile_exists(self):
            raise FileNotFoundError(
                self.name
                + ": "
                + os.path.join(
                    filehandler.determine_migration_dir(self),
                    self.singlefile_to_migrate,
                )
                + " does not exist"
            )
        if not filehandler.self_restore_dir_exists(self):
            raise FileNotFoundError(
                self.name
                + ": "
                + filehandler.determine_migration_dir(self)
                + " does not exist"
            )
