import logging


def list_installed_services(argument_handler):
    if argument_handler.is_list_installed_services_migration_flag_present():
        print("HGello")
        installed_plugins = argument_handler.get_all_plugins_for_installed_services()
        message = 'Installed Services:\n'
        for installed_plugin in installed_plugins:
            message += f'\t{installed_plugin.name} \t[--{installed_plugin.argument}] \t{installed_plugin.help}\n'
        log: logging.Logger = logging.getLogger()
        log.log(logging.INFO, message)