from nislmigrate.migration_error import MigrationError
import pytest

from nislmigrate.systemlink_service_manager import SystemLinkServiceManager


@pytest.mark.unit
def test_capture_services_with_restore_action_captures_plugin() -> None:
    service_manager = SystemLinkServiceManager()

    with pytest.raises(MigrationError):
        service_manager.stop_all_system_link_services()
