from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade
from nislmigrate.migration_action import MigrationAction
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.migration_facilitator import MigrationFacilitator
import pytest


@pytest.mark.unit
def test_capture_services_with_restore_action_captures_plugin():
    facade_factory = FakeFacadeFactory()
    service_migrator = MigrationFacilitator(facade_factory)
    service = TestMigrator()

    service_migrator.migrate([service], MigrationAction.CAPTURE, "")

    assert service.capture_count == 1


@pytest.mark.unit
def test_capture_services_with_restore_action_restores_plugin():
    facade_factory = FakeFacadeFactory()
    service_migrator = MigrationFacilitator(facade_factory)
    service = TestMigrator()

    service_migrator.migrate([service], MigrationAction.RESTORE, "")

    assert service.restore_count == 1


@pytest.mark.unit
def test_capture_services_with_unknown_action_throws_exception():
    facade_factory = FakeFacadeFactory()
    service_migrator = MigrationFacilitator(facade_factory)
    service = TestMigrator()

    with pytest.raises(ValueError):
        service_migrator.migrate([service], "unknown", "")


class TestMigrator(MigratorPlugin):
    capture_count = 0
    restore_count = 0

    @property
    def help(self):
        return ""

    @property
    def name(self):
        return "test"

    @property
    def argument(self):
        return "test"

    def capture(self, mongo_handler=None, file_handler=None):
        self.capture_count += 1

    def restore(self, mongo_handler=None, file_handler=None):
        self.restore_count += 1

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass


class TestSystemLinkServiceManagerFacade(SystemLinkServiceManagerFacade):
    are_services_running = True

    def stop_all_system_link_services(self):
        self.are_services_running = False

    def start_all_system_link_services(self):
        self.are_services_running = True


class TestMongoFacade(MongoFacade):
    is_mongo_running = True

    def start_mongo(self):
        self.is_mongo_running = True

    def stop_mongo(self):
        self.is_mongo_running = False


class TestFileSystemFacade(FileSystemFacade):
    pass


class FakeFacadeFactory(FacadeFactory):
    def __init__(self):
        super().__init__()
        self.mongo_facade: TestMongoFacade = TestMongoFacade()
        self.file_system_facade: TestFileSystemFacade = TestFileSystemFacade()
        self.system_link_service_manager_facade: SystemLinkServiceManagerFacade = TestSystemLinkServiceManagerFacade()

    def get_mongo_facade(self) -> MongoFacade:
        return self.mongo_facade

    def get_file_system_facade(self) -> FileSystemFacade:
        return self.file_system_facade

    def get_system_link_service_manager_facade(self) -> SystemLinkServiceManagerFacade:
        return self.system_link_service_manager_facade
