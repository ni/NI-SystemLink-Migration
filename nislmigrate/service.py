from typing import List, Dict

import nislmigrate.constants as constants
import os
import json
import abc

from nislmigrate.migrators.migrator_factory import MigratorFactory

SERVICE_CONFIGURATION_DIRECTORY = os.path.join(
    constants.program_data_dir, "National Instruments", "Skyline", "Config"
)


class ServicePlugin(abc.ABC):
    """
    Base class for creating a plugin capable of migrating a SystemLink service.
    """

    cached_config = None

    @property
    @abc.abstractmethod
    def names(self) -> List[str]:
        """
        Gets all names for this plugin.
        :return: The plugin names.
        """
        return ["service"]

    @property
    def name(self) -> str:
        """
        Gets the name of this plugin.
        :return: The plugin name.
        """
        # first element of the names list is the default name for argument parsing
        return self.names[0]

    @property
    @abc.abstractmethod
    def help(self) -> str:
        """
        Gets the help string for this service migrator plugin.
        :returns: The help string to display in the command line.
        """
        return "A short sentence describing the operation of the plugin"

    @property
    def config(self) -> Dict[str, str]:
        """
        Gets the configuration dictionary this plugin provides.
        :returns: Gets the configuration dictionary this plugin provides.
        """
        if self.cached_config is None:
            config_file = os.path.join(SERVICE_CONFIGURATION_DIRECTORY, self.name + ".json")
            with open(config_file, encoding="utf-8-sig") as json_file:
                self.cached_config = json.load(json_file)[self.name]
        return self.cached_config

    @abc.abstractmethod
    def capture(self, migration_directory: str, migrator_factory: MigratorFactory) -> None:
        """
        Captures the given service from SystemLink.
        :param migration_directory: the root path to perform the capture to.
        :param migrator_factory: Factory that produces objects capable of doing
                                 actual migration operations.
        """
        pass

    @abc.abstractmethod
    def restore(self, migration_directory: str, migrator_factory: MigratorFactory) -> None:
        """
        Restores the given service to SystemLink.
        :param migration_directory: the root path to perform the restore from.
        :param migrator_factory: Factory that produces objects capable of doing
                                 actual restore operations.
        """
        pass

    def restore_error_check(self,
                            migration_directory: str,
                            migrator_factory: MigratorFactory) -> None:
        """
        Raises a FileNotFoundError if the service anticipates an error migrating.

        :param migration_directory: The directory to migrate to.
        :param migrator_factory: Factory that produces objects capable of doing
                         actual restore operations.
        """
        # TODO: Move this into each service plugin,
        #  since they will want to validate different things.
        file_handler = migrator_factory.get_file_migrator()
        if file_handler is None:
            return
        if not file_handler.migration_dir_exists(migration_directory):
            raise FileNotFoundError(migration_directory + " does not exist")
        if not file_handler.does_file_exist(migration_directory, self):
            migration_directory = file_handler.determine_migration_dir(self)
            path = os.path.join(migration_directory, self.singlefile_to_migrate)
            raise FileNotFoundError(self.name + ": " + path + " does not exist")
        if not file_handler.service_restore_dir_exists(migration_directory, self):
            migration_directory = file_handler.determine_migration_dir(self)
            error = "%s: %s does not exist" % (self.name, migration_directory)
            raise FileNotFoundError(error)
