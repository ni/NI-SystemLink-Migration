import logging
import os
from typing import List, Dict, Any

from argparse import ArgumentParser, Action, SUPPRESS
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_action import MigrationAction
from nislmigrate import migrators
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.extensibility.migrator_plugin_loader import MigratorPluginLoader
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, ArgumentManager

ACTION_ARGUMENT = 'action'
PROGRAM_NAME = 'nislmigrate'
CAPTURE_ARGUMENT = 'capture'
RESTORE_ARGUMENT = 'restore'
ALL_SERVICES_ARGUMENT = 'all'
VERBOSITY_ARGUMENT = 'verbosity'
MIGRATION_DIRECTORY_ARGUMENT = 'dir'
DEFAULT_MIGRATION_DIRECTORY = os.path.expanduser('~\\Documents\\migration')

NO_SERVICES_SPECIFIED_ERROR_TEXT = """

Must specify at least one service to migrate, or migrate all services with the `--all` flag.

Run `nislmigrate capture/restore --help` to list all supported services."""

CAPTURE_OR_RESTORE_NOT_PROVIDED_ERROR_TEXT = 'The "capture" or "restore" argument must be provided'
SERVICE_NOT_INSTALLED_ERROR_TEXT_FORMAT = """

Service '{service_name}' cannot be migrated because the specified service is not installed locally.

Remove unavailable services from the request and try again, or use --all to request all supported services
that are currently installed."""

CAPTURE_COMMAND_HELP = 'use capture to pull data and settings off of a SystemLink server'
RESTORE_COMMAND_HELP = 'use restore to push captured data and settings to a clean SystemLink server'
DIRECTORY_ARGUMENT_HELP = 'specify the directory used for migrated data (defaults to documents)'
ALL_SERVICES_ARGUMENT_HELP = 'use all provided migrator plugins during a capture or restore operation'
FORCE_ARGUMENT_HELP = 'allows capture to delete existing data on the SystemLink server prior to restore'
DEBUG_VERBOSITY_ARGUMENT_HELP = 'print all logged information and stack trace information in case an error occurs'
VERBOSE_VERBOSITY_ARGUMENT_HELP = 'print all logged information except debugging information'


def _get_migrator_arguments_key(migrator: MigratorPlugin):
    return f'{migrator.argument}_args'


def _is_migrator_arguments_key(key: str) -> bool:
    return key.endswith('_args')


class ArgumentHandler:
    """
    Processes arguments either from the command line or just a list of arguments and breaks them
    into the properties required by the migration tool.
    """
    def __init__(
            self,
            arguments: List[str] = None,
            facade_factory: FacadeFactory = FacadeFactory(),
            plugin_loader: MigratorPluginLoader = MigratorPluginLoader(migrators, MigratorPlugin)):
        """
        Creates a new instance of ArgumentHandler
        :param arguments: The list of arguments to process, or None to directly grab CLI arguments.
        :param facade_factory: Factory for migration facades.
        :param plugin_loader: Object that can load migration plugins.
        """
        self.plugin_loader = plugin_loader
        self.facade_factory = facade_factory
        argument_parser = self.__create_migration_tool_argument_parser()
        if arguments is None:
            self.parsed_arguments = argument_parser.parse_args()
        else:
            self.parsed_arguments = argument_parser.parse_args(arguments)

    def get_list_of_services_to_capture_or_restore(self) -> List[MigratorPlugin]:
        """
        Generate a list of migration strategies to use during migration,
        based on the given arguments.

        :return: A list of selected migration actions.
        """
        migrate_all = self.__is_all_service_migration_flag_present()
        enabled_plugins = (self.__get_all_plugins_for_installed_services()
                           if migrate_all
                           else self.__get_enabled_plugins())
        if len(enabled_plugins) == 0:
            raise MigrationError(NO_SERVICES_SPECIFIED_ERROR_TEXT)
        if not migrate_all:
            self.__verify_service_is_installed_for_plugins(enabled_plugins)
        return [plugin for plugin in enabled_plugins]

    def get_migrator_additional_arguments(self, migrator: MigratorPlugin) -> Dict[str, Any]:
        """
        Gets the additional command line arguments for the specified migrator.

        :param migrator: The migrator for which to get arguments.
        :return: A dictionary where the keys are the names of the additional arguments for the migrator,
                 and the values are the argument values.
        """
        key = _get_migrator_arguments_key(migrator)
        return getattr(self.parsed_arguments, key, {})

    def __get_all_plugins_for_installed_services(self) -> List[MigratorPlugin]:
        return [plugin for plugin in self.plugin_loader.get_plugins()
                if plugin.is_service_installed(self.facade_factory)]

    def __get_enabled_plugins(self) -> List[MigratorPlugin]:
        arguments: List[str] = self.__get_enabled_plugin_arguments()
        return [self.__find_plugin_for_argument(argument) for argument in arguments]

    def __get_enabled_plugin_arguments(self) -> List[str]:
        arguments = vars(self.parsed_arguments)
        plugin_arguments: List[str] = self.__remove_non_plugin_arguments(arguments)
        return [argument for argument in plugin_arguments if self.__is_plugin_enabled(argument)]

    def __find_plugin_for_argument(self, argument: str) -> MigratorPlugin:
        plugins = self.plugin_loader.get_plugins()
        plugin = [plugin for plugin in plugins if plugin.argument == argument][0]
        return plugin

    def __verify_service_is_installed_for_plugins(self, plugins: List[MigratorPlugin]):
        for plugin in plugins:
            if not plugin.is_service_installed(self.facade_factory):
                message = SERVICE_NOT_INSTALLED_ERROR_TEXT_FORMAT.format(service_name=plugin.name)
                raise MigrationError(message)

    def __is_plugin_enabled(self, plugin_argument: str) -> bool:
        return getattr(self.parsed_arguments, plugin_argument)

    def __is_all_service_migration_flag_present(self) -> bool:
        return getattr(self.parsed_arguments, ALL_SERVICES_ARGUMENT)

    def is_force_migration_flag_present(self) -> bool:
        return getattr(self.parsed_arguments, 'force', False)

    @staticmethod
    def __remove_non_plugin_arguments(arguments: Dict[str, Any]) -> List[str]:
        return [
            argument
            for argument in arguments
            if not argument == ACTION_ARGUMENT
            and not argument == MIGRATION_DIRECTORY_ARGUMENT
            and not argument == ALL_SERVICES_ARGUMENT
            and not argument == VERBOSITY_ARGUMENT
            and not argument == 'force'
            and not _is_migrator_arguments_key(argument)
        ]

    def get_migration_action(self) -> MigrationAction:
        """Determines whether to capture or restore based on the arguments.

        :return: MigrationAction.RESTORE or MigrationAction.CAPTURE.
        """
        if self.parsed_arguments.action == RESTORE_ARGUMENT:
            return MigrationAction.RESTORE
        elif self.parsed_arguments.action == CAPTURE_ARGUMENT:
            return MigrationAction.CAPTURE
        else:
            raise MigrationError(CAPTURE_OR_RESTORE_NOT_PROVIDED_ERROR_TEXT)

    def get_migration_directory(self) -> str:
        """Gets the migration directory path based on the parsed arguments.

        :return: The migration directory path from the arguments,
                 or the default if none was specified.
        """
        argument = MIGRATION_DIRECTORY_ARGUMENT
        default = DEFAULT_MIGRATION_DIRECTORY
        return getattr(self.parsed_arguments, argument, default)

    def get_logging_verbosity(self) -> int:
        """Gets the level with which to logged based on the parsed command line arguments.

        :return: The configured verbosity as an integer.
        """
        return self.parsed_arguments.verbosity

    def __create_migration_tool_argument_parser(self) -> ArgumentParser:
        """Creates an argparse parser that knows how to parse the migration
           tool's command line arguments.

        :return: The built parser.
        """
        description = 'Run `nislmigrate {command} -h` to list additional options.'
        argument_parser = ArgumentParser(prog=PROGRAM_NAME, description=description)
        self.__add_logging_flag_options(argument_parser)
        self.__add_capture_and_restore_commands(argument_parser)
        return argument_parser

    def __add_capture_and_restore_commands(self, argument_parser: ArgumentParser):
        parent_parser: ArgumentParser = ArgumentParser(add_help=False)
        self.__add_logging_flag_options(parent_parser)
        self.__add_additional_flag_options(parent_parser)
        self.__add_plugin_arguments(parent_parser)

        sub_parser = argument_parser.add_subparsers(dest=ACTION_ARGUMENT, metavar='command')
        sub_parser.add_parser(CAPTURE_ARGUMENT, help=CAPTURE_COMMAND_HELP, parents=[parent_parser])
        restore_parser = sub_parser.add_parser(RESTORE_ARGUMENT, help=RESTORE_COMMAND_HELP, parents=[parent_parser])
        restore_parser.add_argument(
            '-f',
            '--force',
            help=FORCE_ARGUMENT_HELP,
            action='store_true')

    @staticmethod
    def __add_additional_flag_options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--' + MIGRATION_DIRECTORY_ARGUMENT,
            help=DIRECTORY_ARGUMENT_HELP,
            default=DEFAULT_MIGRATION_DIRECTORY,
        )
        parser.add_argument(
            '--' + ALL_SERVICES_ARGUMENT,
            help=ALL_SERVICES_ARGUMENT_HELP,
            action='store_true')

    @staticmethod
    def __add_logging_flag_options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '-d',
            '--debug',
            help=DEBUG_VERBOSITY_ARGUMENT_HELP,
            action='store_const',
            dest=VERBOSITY_ARGUMENT,
            const=logging.DEBUG,
            default=logging.WARNING)
        parser.add_argument(
            '-v',
            '--verbose',
            help=VERBOSE_VERBOSITY_ARGUMENT_HELP,
            action='store_const',
            dest=VERBOSITY_ARGUMENT,
            const=logging.INFO)

    def __add_plugin_arguments(self, parser: ArgumentParser) -> None:
        """Adds expected arguments to the parser for all migrators.

        :param parser: The parser to add the argument flag to.
        """
        for plugin in self.plugin_loader.get_plugins():
            manager = _MigratorArgumentManager(plugin, parser)
            parser.add_argument(
                '--' + plugin.argument,
                help=plugin.help,
                action='store_true',
                dest=plugin.argument)
            plugin.add_additional_arguments(manager)


class _MigratorArgumentManager(ArgumentManager):
    def __init__(self, plugin: MigratorPlugin, parser: ArgumentParser):
        self.__parser = parser
        self.__plugin = plugin

    def add_switch(self, name: str, help: str) -> None:
        migrator_argument = self.__plugin.argument
        argument = f'--{migrator_argument}-{name}'
        dest = f'{_get_migrator_arguments_key(self.__plugin)}.{name}'
        self.__parser.add_argument(
                argument,
                nargs=0,
                help=help,
                action=_StoreMigratorSwitchAction,
                dest=dest,
                default=SUPPRESS)


class _StoreMigratorSwitchAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        dest, key = self.dest.split('.', 1)
        args = getattr(namespace, dest, {})
        args[key] = True
        setattr(namespace, dest, args)
