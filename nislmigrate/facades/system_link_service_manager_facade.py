import subprocess
import logging
from typing import List
from nislmigrate.logs.migration_error import MigrationError

STOP_SERVICE_MANAGER_COMMAND = 'net.exe stop "NI Skyline Service Manager" /y'
START_SERVICE_MANAGER_COMMAND = 'net.exe start "NI Skyline Service Manager" /y'


class SystemLinkServiceManagerFacade:
    """
    Manages SystemLink services by invoking the SystemLink command line configuration utility.
    """
    def stop_all_system_link_services(self) -> None:
        """
        Stops all SystemLink services.
        """
        log = logging.getLogger(SystemLinkServiceManagerFacade.__name__)
        log.log(logging.INFO, 'Stopping all SystemLink services...')
        self.__run_command(STOP_SERVICE_MANAGER_COMMAND, [2])

    def start_all_system_link_services(self) -> None:
        """
        Starts all SystemLink services.
        """
        log = logging.getLogger(SystemLinkServiceManagerFacade.__name__)
        log.log(logging.INFO, 'Starting all SystemLink services...')
        self.__run_command(START_SERVICE_MANAGER_COMMAND, [])

    @staticmethod
    def __run_command(command: str, allowedErrorCodes: List[int]):
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            if e.returncode in allowedErrorCodes:
                return
            descriptions = (str(e), repr(e.stderr).replace('\\n', '\n').replace('\\r', '\r'))
            error_string = 'NISystemLinkServerConfigCmd.exe encountered an error:\n\n%s\n\n%s'
            raise MigrationError(error_string % descriptions)
