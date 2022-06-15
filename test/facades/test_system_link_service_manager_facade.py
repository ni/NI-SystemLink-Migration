from unittest.mock import patch, Mock
from nislmigrate.facades import system_link_service_manager_facade
from nislmigrate.logs.migration_error import MigrationError

import subprocess
import pytest

from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade


@pytest.mark.unit
@patch('subprocess.run')
def test_stop_all_system_link_services_when_configuration_tool_installed(run: Mock) -> None:
    service_manager = SystemLinkServiceManagerFacade()

    service_manager.stop_all_system_link_services()

    run.assert_called_with(
        system_link_service_manager_facade.STOP_SERVICE_MANAGER_COMMAND,
        check=True,
        capture_output=True,
    )


@pytest.mark.unit
@patch('subprocess.run')
def test_start_all_system_link_services_when_configuration_tool_installed(run: Mock) -> None:
    service_manager = SystemLinkServiceManagerFacade()

    service_manager.start_all_system_link_services()

    run.assert_called_with(
        system_link_service_manager_facade.START_SERVICE_MANAGER_COMMAND,
        check=True,
        capture_output=True,
    )


@pytest.mark.unit
@patch('subprocess.run')
def test_stop_all_system_link_services_succeeds_when_services_already_stopped_error_occurs(run: Mock) -> None:
    run.side_effect = subprocess.CalledProcessError(returncode=2, cmd=['cmd'])
    service_manager = SystemLinkServiceManagerFacade()

    service_manager.stop_all_system_link_services()


@pytest.mark.unit
@patch('subprocess.run')
def test_stop_all_system_link_services_fails_when_other_error_occurs(run: Mock) -> None:
    run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=['cmd'])
    service_manager = SystemLinkServiceManagerFacade()

    with pytest.raises(MigrationError):
        service_manager.stop_all_system_link_services()
