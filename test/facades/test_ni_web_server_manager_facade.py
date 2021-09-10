
from nislmigrate.facades import ni_web_server_manager_facade
from nislmigrate.facades.ni_web_server_manager_facade import NiWebServerManagerFacade
from unittest.mock import patch, Mock

from nislmigrate.logs.migration_error import MigrationError
import pytest


@pytest.mark.unit
@patch('os.path.exists')
def test_restart_web_server_when_configuration_tool_not_installed(exists) -> None:
    manager = NiWebServerManagerFacade()
    exists.return_value = False

    with pytest.raises(MigrationError):
        manager.restart_web_server()


@pytest.mark.unit
@patch('subprocess.run')
@patch('os.path.exists')
def test_restart_web_server_when_configuration_tool_installed(exists: Mock, run: Mock) -> None:
    manager = NiWebServerManagerFacade()
    exists.return_value = True

    manager.restart_web_server()

    run.assert_called_with(
        ni_web_server_manager_facade.RESTART_COMMAND,
        check=True,
        capture_output=True,
    )
