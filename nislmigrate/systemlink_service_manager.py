"""Handle Service Manager operations."""

import subprocess
import os
from nislmigrate import constants

CONFIGURATION_EXECUTABLE_PATH = os.path.join(
    constants.program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NISystemLinkServerConfigCmd.exe",
)
STOP_ALL_SERVICES_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " stop-all-services wait "
START_ALL_SERVICES_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " start-all-services wait "
STOP_SERVICE_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " stop-service "
START_SERVICE_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " start-service "


class SystemLinkServiceManager:
    """
    Manages SystemLink services by invoking the SystemLink command line configuration utility.
    """
    def stop_sl_service(self, service) -> None:
        """
        Stops given SystemLink service.
        :param service: The service to stop.
        """
        if service.require_service_restart:
            print("Stopping " + service.service_to_restart + " service")
            subprocess.run(
                STOP_SERVICE_COMMAND + service.service_to_restart + " wait",
                check=True,
            )
            subprocess.run(STOP_ALL_SERVICES_COMMAND, check=True)

    def stop_all_sl_services(self) -> None:
        """
        Stops all SystemLink services.
        """
        print("Stopping all SystemLink services...")
        subprocess.run(STOP_ALL_SERVICES_COMMAND, check=True)

    def start_all_sl_services(self) -> None:
        """
        Starts all SystemLink services.
        """
        print("Starting all SystemLink services")
        subprocess.run(START_ALL_SERVICES_COMMAND, check=True)
