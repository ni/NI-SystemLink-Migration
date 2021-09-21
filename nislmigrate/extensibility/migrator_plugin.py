from typing import Dict, Any, Optional

import os
import abc

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.utility.paths import get_ni_application_data_directory_path


DEFAULT_SERVICE_CONFIGURATION_DIRECTORY: str = os.path.join(
    get_ni_application_data_directory_path(),
    'Skyline',
    'Config')


class ArgumentManager(abc.ABC):
    """
    Abstracts management of migrator-specific command line arguments.
    """

    @abc.abstractmethod
    def add_switch(self, name: str, help: str) -> None:
        """
        Adds a switch command line argument that will be associated with a migrator_plugin.
        The argument will be namespaced by the migrator name in order to ensure that it does
        not conflict with any other arguments, resulting in a command line argument in the form:

          --<migrator-name>-<argument-name>

        If the switch is specified on the command line, the arguments dictionary passed to the
        migrator's create/restore/pre_restore_check methods contain the <argument-name>
        with a value of True. Otherwise <argument-name> will not be in the dictionary.
        """
        raise NotImplementedError


class MigratorPlugin(abc.ABC):
    """
    Base class for creating a plugin capable of migrating a SystemLink service.
    """

    service_configuration_directory: str = DEFAULT_SERVICE_CONFIGURATION_DIRECTORY
    __cached_config: Optional[Dict[str, Any]] = None

    @property
    @abc.abstractmethod
    def argument(self) -> str:
        """
        Gets the string to be used as the argument for using this migrator from the command line.
        :return: The argument.
        """
        return 'service'

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Gets the name of this plugin. This needs to be the exact name of the
        configuration file for this service if it has one.
        :return: The plugin name.
        """
        return 'The full name of the plugin'

    @property
    @abc.abstractmethod
    def help(self) -> str:
        """
        Gets the help string for this service migrator plugin.
        :returns: The help string to display in the command line.
        """
        return 'A short sentence describing the operation of the plugin'

    def config(self, facade_factory: FacadeFactory) -> Dict[str, Any]:
        """
        Gets the configuration dictionary this plugin provides.
        :param facade_factory: Factory that produces objects abstracing away operations.
        :returns: Gets the configuration dictionary this plugin provides.
        """
        if self.__cached_config is None:
            config_file = self.__build_config_file_path()
            filesystem_facade = facade_factory.get_file_system_facade()
            self.__cached_config = filesystem_facade.read_json_file(config_file)[self.name]
        return self.__cached_config

    @abc.abstractmethod
    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]) -> None:
        """
        Captures the given service from SystemLink.
        :param migration_directory: the root path to perform the capture to.
        :param facade_factory: Factory that produces objects capable of doing
                                 actual migration operations.
        :param arguments: Dictionary containing any command line argument values defined in add_additional_arguments.
        """
        pass

    @abc.abstractmethod
    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]) -> None:
        """
        Restores the given service to SystemLink.
        :param migration_directory: the root path to perform the restore from.
        :param facade_factory: Factory that produces objects capable of doing
                                 actual restore operations.
        :param arguments: Dictionary containing any command line argument values defined in add_additional_arguments.
        """
        pass

    @abc.abstractmethod
    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        """
        Raises a MigrationError if the service anticipates an error restoring.

        :param migration_directory: The directory to migrate to.
        :param facade_factory: Factory that produces objects capable of doing
                         actual restore operations.
        :param arguments: Dictionary containing any command line argument values defined in add_additional_arguments.
        """
        pass

    def pre_capture_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        """
        Raises a MigrationError if the service anticipates an error capturing.

        :param migration_directory: The directory to migrate to.
        :param facade_factory: Factory that produces objects capable of doing
                         actual restore operations.
        :param arguments: Dictionary containing any command line argument values defined in add_additional_arguments.
        """
        pass

    def is_service_installed(self, facade_factory: FacadeFactory) -> bool:
        """
        Checks whether the service corresponding to a given migrator is installed locally.

        :param facade_factory: Factory for migration facades.
        :return: True if the service is installed.
        """
        return facade_factory.file_system_facade.does_file_exist(self.__build_config_file_path())

    def add_additional_arguments(self, argument_manager: ArgumentManager) -> None:
        """
        Adds additional command line arguments to control the behavior of the migration.
        The from the command line values will be passed to capture / restore / pre_restore_check.

        :param argument_mananger: API for adding arguments to this MigratorPlugin.
        """
        pass

    def __build_config_file_path(self) -> str:
        return os.path.join(self.service_configuration_directory, self.name + '.json')
