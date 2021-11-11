import logging
from typing import List

from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin


class InformationLogger:
    """
    Utility methods to add formatted information to the log.
    """
    @staticmethod
    def list_installed_services(argument_handler: ArgumentHandler):
        """
        Lists the services the migration tool recognises as installed.

        :param argument_handler: Handler for the command line arguments.
        """
        installed_plugins: List[MigratorPlugin] = argument_handler.get_all_plugins_for_installed_services()
        message: str = 'Installed Services:\n'
        installed_plugin: MigratorPlugin
        for installed_plugin in installed_plugins:
            message += f'\t{installed_plugin.name} \t[--{installed_plugin.argument}] \t{installed_plugin.help}\n'
        log: logging.Logger = logging.getLogger()
        log.log(logging.INFO, message)
