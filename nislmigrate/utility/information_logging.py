import logging

from nislmigrate.logs.migration_error import MigrationError


def list_installed_services_and_raise_if_capture_or_restore_present(argument_handler):
    print("false")
    if argument_handler.is_list_installed_services_migration_flag_present():
        print("true")
        list_installed_services(argument_handler)
        migration_specified = False
        try:
            argument_handler.get_migration_action()
            migration_specified = True
        except MigrationError:
            migration_specified = False
        if migration_specified:
            raise MigrationError('Remove the `--list-installed-services` flag to actually run the migration.')
        exit()


def list_installed_services(argument_handler):

    if argument_handler.is_list_installed_services_migration_flag_present():
        installed_plugins = argument_handler.get_all_plugins_for_installed_services()
        message = 'Installed Services:\n'
        for installed_plugin in installed_plugins:
            message += f'\t{installed_plugin.name} \t[--{installed_plugin.argument}] \t{installed_plugin.help}\n'
        log: logging.Logger = logging.getLogger()
        log.log(logging.INFO, message)
