"""Handle Service Manager operations."""

import subprocess
import os
from nislmigrate import constants
from nislmigrate.migration_error import MigrationError

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
    def stop_all_systemlink_services(self) -> None:
        """
        Stops all SystemLink services.
        """
        print("Stopping all SystemLink services...")
        self.__verify_configuration_tool_is_installed()
        self.__run_command(STOP_ALL_SERVICES_COMMAND)

    def start_all_systemlink_services(self) -> None:
        """
        Starts all SystemLink services.
        """
        print("Starting all SystemLink services")
        self.__verify_configuration_tool_is_installed()
        self.__run_command(START_ALL_SERVICES_COMMAND)

    def __run_command(self, command: str):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            descriptions = (str(e), repr(e.stderr).replace("\\n", "\n").replace("\\r", "\r"))
            raise MigrationError("NISystemLinkServerConfigCmd.exe encountered an error:\n\n%s\n\n%s" % descriptions)

    def __verify_configuration_tool_is_installed(self):
        if not os.path.exists(CONFIGURATION_EXECUTABLE_PATH):
            error = "Unable to locate SystemLink server configuration tool at '%s'" % CONFIGURATION_EXECUTABLE_PATH
            raise MigrationError(error)
