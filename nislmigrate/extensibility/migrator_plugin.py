from typing import Dict, Any, Optional

import os
import abc

from nislmigrate.facades.facade_factory import FacadeFactory

SERVICE_CONFIGURATION_DIRECTORY = os.path.join(
    str(os.environ.get("ProgramData")),
    "National Instruments",
    "Skyline",
    "Config")


class MigratorPlugin(abc.ABC):
    """
    Base class for creating a plugin capable of migrating a SystemLink service.
    """

    __cached_config: Optional[Dict[str, Any]] = None

    @property
    @abc.abstractmethod
    def argument(self) -> str:
        """
        Gets the string to be used as the argument for using this migrator from the command line.
        :return: The argument.
        """
        return "service"

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Gets the name of this plugin. This needs to be the exact name of the
        configuration file for this service if it has one.
        :return: The plugin name.
        """
        return "The full name of the plugin"

    @property
    @abc.abstractmethod
    def help(self) -> str:
        """
        Gets the help string for this service migrator plugin.
        :returns: The help string to display in the command line.
        """
        return "A short sentence describing the operation of the plugin"

    def config(self, facade_factory: FacadeFactory) -> Dict[str, Any]:
        """
        Gets the configuration dictionary this plugin provides.
        :param facade_factory: Factory that produces objects abstracing away operations.
        :returns: Gets the configuration dictionary this plugin provides.
        """
        if self.__cached_config is None:
            config_file = os.path.join(SERVICE_CONFIGURATION_DIRECTORY, self.name + ".json")
            filesystem_facade = facade_factory.get_file_system_facade()
            self.__cached_config = filesystem_facade.read_json_file(config_file)[self.name]
        return self.__cached_config

    @abc.abstractmethod
    def capture(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        """
        Captures the given service from SystemLink.
        :param migration_directory: the root path to perform the capture to.
        :param facade_factory: Factory that produces objects capable of doing
                                 actual migration operations.
        """
        pass

    @abc.abstractmethod
    def restore(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        """
        Restores the given service to SystemLink.
        :param migration_directory: the root path to perform the restore from.
        :param facade_factory: Factory that produces objects capable of doing
                                 actual restore operations.
        """
        pass

    @abc.abstractmethod
    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        """
        Raises a MigrationError if the service anticipates an error migrating.

        :param migration_directory: The directory to migrate to.
        :param facade_factory: Factory that produces objects capable of doing
                         actual restore operations.
        """
        pass
