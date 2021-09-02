import subprocess
import os
import logging
from nislmigrate.logs.migration_error import MigrationError

CONFIGURATION_EXECUTABLE_PATH = os.path.join(
    str(os.environ.get("ProgramW6432")),
    "National Instruments",
    "Shared",
    "Skyline",
    "NISystemLinkServerConfigCmd.exe",
)
STOP_ALL_SERVICES_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " stop-all-services wait "
START_ALL_SERVICES_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " start-all-services wait "
STOP_SERVICE_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " stop-service "
START_SERVICE_COMMAND = CONFIGURATION_EXECUTABLE_PATH + " start-service "


class SystemLinkServiceManagerFacade:
    """
    Manages SystemLink services by invoking the SystemLink command line configuration utility.
    """
    def stop_all_system_link_services(self) -> None:
        """
        Stops all SystemLink services.
        """
        log = logging.getLogger(SystemLinkServiceManagerFacade.__name__)
        log.log(logging.INFO, "Stopping all SystemLink services...")
        self.__run_command(STOP_ALL_SERVICES_COMMAND)

    def start_all_system_link_services(self) -> None:
        """
        Starts all SystemLink services.
        """
        log = logging.getLogger(SystemLinkServiceManagerFacade.__name__)
        log.log(logging.INFO, "Starting all SystemLink services...")
        self.__run_command(START_ALL_SERVICES_COMMAND)

    def __run_command(self, command: str):
        self.__verify_configuration_tool_is_installed()
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            descriptions = (str(e), repr(e.stderr).replace("\\n", "\n").replace("\\r", "\r"))
            error_string = "NISystemLinkServerConfigCmd.exe encountered an error:\n\n%s\n\n%s"
            raise MigrationError(error_string % descriptions)

    @staticmethod
    def __verify_configuration_tool_is_installed():
        if not os.path.exists(CONFIGURATION_EXECUTABLE_PATH):
            error_string = "Unable to locate SystemLink server configuration tool at '%s'"
            raise MigrationError(error_string % CONFIGURATION_EXECUTABLE_PATH)
