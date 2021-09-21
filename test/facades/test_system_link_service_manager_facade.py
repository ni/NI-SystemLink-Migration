from unittest.mock import patch, Mock

from nislmigrate.facades import system_link_service_manager_facade
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
