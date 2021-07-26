import slmigrate.constants as constants
import os
import json
import functools

from abc import ABC, abstractmethod


class ServicePlugin(ABC):

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

    @functools.cached_property
    def config(self):
        # most (all?) services use this style of config file.  Plugins won't need to override this method.
        config_file = os.path.join(constants.service_config_dir, self.name + ".json")
        with open(config_file, encoding="utf-8-sig") as json_file:
            return json.load(json_file)

    @abstractmethod
    def capture(self, mongohandler=None, filehandler=None):
        pass

    @abstractmethod
    def restore(self, mongohandler=None, filehandler=None):
        pass

    @abstractmethod
    def restore_error_check(self, mongohandler=None, filehandler=None):
        """TODO: Complete documentation.

        :param service:
        :return:
        """
        if not filehandler.migration_dir_exists(constants.migration_dir):
            raise FileNotFoundError(constants.migration_dir + " does not exist")
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
