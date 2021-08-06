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
        # first element of the names list is the default name for argument parsing
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
        return self.cached_config

    @abstractmethod
    def capture(self, mongo_handler=None, file_handler=None):
        """
        Captures the given service from SystemLink.

        :param mongo_handler: An object capable of performing mongo database operations.
        :param file_handler: An object capable of performing file operations.
        """
        pass

    @abstractmethod
    def restore(self, mongo_handler=None, file_handler=None):
        """
        Restores the given service to SystemLink.

        :param mongo_handler: An object capable of performing mongo database operations.
        :param file_handler: An object capable of performing file operations.
        """
        pass

    def restore_error_check(self, migration_directory: str, mongo_handler=None, file_handler=None):
        """
        Raises a FileNotFoundError if the service anticipates an error migrating.

        :param migration_directory: The directory to migrate to.
        :param mongo_handler: An object capable of performing mongo database operations.
        :param file_handler: An object capable of performing file operations.
        """
        if file_handler is None:
            return
        if not file_handler.migration_dir_exists(migration_directory):
            raise FileNotFoundError(migration_directory + " does not exist")
        if not file_handler.service_restore_singlefile_exists(migration_directory, self):
            path = os.path.join(file_handler.determine_migration_dir(self), self.singlefile_to_migrate)
            raise FileNotFoundError(self.name + ": " + path + " does not exist")
        if not file_handler.service_restore_dir_exists(migration_directory, self):
            raise FileNotFoundError(self.name + ": " + file_handler.determine_migration_dir(self) + " does not exist")
