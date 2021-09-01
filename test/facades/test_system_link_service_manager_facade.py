from unittest.mock import patch, Mock

from nislmigrate.facades import system_link_service_manager_facade
from nislmigrate.logs.migration_error import MigrationError
import pytest

from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade


@pytest.mark.unit
@patch('os.path.exists')
def test_stop_all_system_link_services_when_configuration_tool_not_installed(exists) -> None:
    service_manager = SystemLinkServiceManagerFacade()
    exists.return_value = False

    with pytest.raises(MigrationError):
        service_manager.stop_all_system_link_services()


@pytest.mark.unit
@patch('os.path.exists')
@patch('subprocess.run')
def test_stop_all_system_link_services_when_configuration_tool_installed(exists: Mock, run: Mock) -> None:
    service_manager = SystemLinkServiceManagerFacade()
    exists.return_value = True

    service_manager.stop_all_system_link_services()

    run.verify_called(system_link_service_manager_facade.STOP_ALL_SERVICES_COMMAND)


@pytest.mark.unit
@patch('os.path.exists')
def test_start_all_system_link_services_when_configuration_tool_not_installed(exists) -> None:
    service_manager = SystemLinkServiceManagerFacade()
    exists.return_value = False

    with pytest.raises(MigrationError):
        service_manager.start_all_system_link_services()


@pytest.mark.unit
@patch('os.path.exists')
@patch('subprocess.run')
def test_start_all_system_link_services_when_configuration_tool_installed(exists: Mock, run: Mock) -> None:
    service_manager = SystemLinkServiceManagerFacade()
    exists.return_value = True

    service_manager.start_all_system_link_services()

    run.verify_called(system_link_service_manager_facade.START_ALL_SERVICES_COMMAND)
