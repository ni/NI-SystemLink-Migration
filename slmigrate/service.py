import slmigrate.constants as constants
import os, json

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

    @property
    def service_config(self):
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
