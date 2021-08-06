"""Handle Service Manager operations."""

import subprocess

from slmigrate import constants


class SystemLinkServiceManager:
    """
    Manages SystemLink services by invoking the SystemLink command line configuration utility.
    """
    def stop_sl_service(self, service):
        """
        Stops given SystemLink service.

        :param service: The service to stop.
        :return: None.
        """
        if service.require_service_restart:
            print("Stopping " + service.service_to_restart + " service")
            subprocess.run(
                constants.slconf_cmd_stop_service + service.service_to_restart + " wait",
                check=True,
            )
            subprocess.run(constants.slconf_cmd_stop_all, check=True)

    def stop_all_sl_services(self):
        """
        Stops all SystemLink services.

        :return: None.
        """
        print("Stopping all SystemLink services...")
        subprocess.run(constants.slconf_cmd_stop_all, check=True)

    def start_all_sl_services(self):
        """
        Starts all SystemLink services.

        :return: None.
        """
        print("Starting all SystemLink services")
        subprocess.run(constants.slconf_cmd_start_all, check=True)
