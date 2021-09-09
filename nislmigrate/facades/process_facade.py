import os
import subprocess
from typing import List


class ProcessError(Exception):
    def __init__(self, error: str):
        self.error: str = error


class BackgroundProcess:
    def __init__(self, arguments):
        """
        Creates and starts the background process

        :param arguments: The name of the process to run and the arguments to pass.
        """

        self._arguments = arguments
        self._process_handle: subprocess.Popen = subprocess.Popen(
                arguments,
                env=os.environ,
                creationflags=subprocess.CREATE_NEW_CONSOLE)

    def __del__(self):
        self.stop()

    def stop(self):
        """
        Stops the background process if it is running
        """

        if self._process_handle:
            actual_handle: subprocess.Popen = self._process_handle
            subprocess.Popen.kill(actual_handle)
            self._process_handle = None


class ProcessFacade:
    def run_process(self, arguments: List[str]) -> str:
        """
        Runs a command.

        :param arguments: The name of the process to run and the arguments to pass.
        :raises:
            ProcessError if the process returns an error.
        """

        try:
            result = subprocess.check_output(arguments, stderr=subprocess.STDOUT)
            return result.decode('utf-8')
        except subprocess.CalledProcessError as e:
            raise ProcessError(e.stderr) from e

    def run_background_process(self, arguments: List[str]) -> BackgroundProcess:
        return BackgroundProcess(arguments)
