import logging

from nislmigrate.logs.migration_error import MigrationError


def should_list_installed_services(argument_handler):
    return argument_handler.is_list_installed_services_migration_flag_present()


def is_migration_action_present(argument_handler):
    try:
        argument_handler.get_migration_action()
        return True
    except MigrationError:
        return False


def list_installed_services(argument_handler):
    if argument_handler.is_list_installed_services_migration_flag_present():
        installed_plugins = argument_handler.get_all_plugins_for_installed_services()
        message = 'Installed Services:\n'
        for installed_plugin in installed_plugins:
            message += f'\t{installed_plugin.name} \t[--{installed_plugin.argument}] \t{installed_plugin.help}\n'
        log: logging.Logger = logging.getLogger()
        log.log(logging.INFO, message)
