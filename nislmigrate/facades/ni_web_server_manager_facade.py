import os
import logging
import subprocess
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.utility.paths import get_ni_shared_directory_64_path

CONFIGURATION_EXECUTABLE_PATH = os.path.join(
    get_ni_shared_directory_64_path(),
    'Web Server Config',
    'NIWebServerConfigurationCmd.exe',
)
RESTART_COMMAND = CONFIGURATION_EXECUTABLE_PATH + ' control restart'


class NiWebServerManagerFacade:
    """Manages the NI Web Server using the command line configuration utility."""
    def restart_web_server(self):
        """Restarts the NI Web Server"""
        log = logging.getLogger(NiWebServerManagerFacade.__name__)
        log.log(logging.INFO, 'Restarting the NI Web Server...')
        self.__run_command(RESTART_COMMAND)

    def __run_command(self, command: str):
        self.__verify_configuration_tool_is_installed()
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            descriptions = (str(e), repr(e.stderr).replace('\\n', '\n').replace('\\r', '\r'))
            error_string = 'NIWebServerConfigurationCmd.exe encountered an error:\n\n%s\n\n%s'
            raise MigrationError(error_string % descriptions)

    def __verify_configuration_tool_is_installed(self):
        if not os.path.exists(CONFIGURATION_EXECUTABLE_PATH):
            error_string = 'Unable to locate NI Web Server configuration tool at "%s"'
            raise MigrationError(error_string % CONFIGURATION_EXECUTABLE_PATH)
