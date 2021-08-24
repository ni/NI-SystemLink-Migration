import pytest

from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.argument_handler import RESTORE_ARGUMENT
from nislmigrate.argument_handler import MIGRATION_DIRECTORY_ARGUMENT
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_facilitator import MigrationFacilitator
from nislmigrate.facades.systemlink_service_manager import SystemLinkServiceManager
from test import test_constants


@pytest.mark.unit
def test_missing_migration_directory() -> None:
    test_arguments = [
        RESTORE_ARGUMENT,
        "--tag",
        "--" + MIGRATION_DIRECTORY_ARGUMENT + "=" + test_constants.migration_dir,
    ]

    argument_handler = ArgumentHandler(test_arguments)

    migrator_factory = FacadeFactory()
    migrator = MigrationFacilitator(migrator_factory, FakeServiceManager())

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
    migration_action = argument_handler.determine_migration_action()
    migration_directory = argument_handler.get_migration_directory()

    with pytest.raises(FileNotFoundError):
        migrator.migrate(services_to_migrate, migration_action, migration_directory)


@pytest.mark.unit
def test_missing_service_migration_file() -> None:
    test_arguments = [
        RESTORE_ARGUMENT,
        "--tag",
        "--" + MIGRATION_DIRECTORY_ARGUMENT + "=" + test_constants.migration_dir,
    ]

    argument_handler = ArgumentHandler(test_arguments)

    migrator_factory = FacadeFactory()
    migrator = MigrationFacilitator(migrator_factory, FakeServiceManager())

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
    migration_action = argument_handler.determine_migration_action()
    migration_directory = argument_handler.get_migration_directory()

    with pytest.raises(FileNotFoundError):
        migrator.migrate(services_to_migrate, migration_action, migration_directory)


class FakeServiceManager(SystemLinkServiceManager):
    are_services_running = True

    def stop_all_system_link_services(self) -> None:
        self.are_services_running = False

    def start_all_system_link_services(self) -> None:
        self.are_services_running = True
