"""Handle Service Manager operations."""

import subprocess

from slmigrate import constants


def stop_sl_service(service):
    """TODO: Complete documentation.

    :param service:
    :return:
    """
    if service.require_service_restart:
        print("Stopping " + service.service_to_restart + " service")
        subprocess.run(
            constants.slconf_cmd_stop_service + service.service_to_restart + " wait",
            check=True,
        )
        subprocess.run(constants.slconf_cmd_stop_all, check=True)


def stop_all_sl_services():
    """TODO: Complete documentation.

    :return:
    """
    print("Stopping all SystemLink services...")
    subprocess.run(constants.slconf_cmd_stop_all, check=True)


def start_all_sl_services():
    """TODO: Complete documentation.

    :return:
    """
    print("Starting all SystemLink services")
    subprocess.run(constants.slconf_cmd_start_all, check=True)
