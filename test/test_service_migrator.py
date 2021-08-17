from nislmigrate.migration_action import MigrationAction
from nislmigrate.migrator_factory import MigratorFactory
from nislmigrate.mongo_migrator import MongoMigrator
from nislmigrate.service import ServicePlugin
from nislmigrate.migration_facilitator import MigrationFacilitator
import pytest


@pytest.mark.unit
def test_capture_services_with_restore_action_captures_plugin():
    migrator_factory = MigratorFactory()
    service_migrator = MigrationFacilitator(migrator_factory)
    service_migrator.service_manager = TestServiceManagerHandler()
    service_migrator.mongo_handler = TestMongoMigrator()
    service = TestMigratorPlugin()

    service_migrator.migrate([service], MigrationAction.CAPTURE, "")

    assert service.capture_count == 1


@pytest.mark.unit
def test_capture_services_with_restore_action_restores_plugin():
    migrator_factory = MigratorFactory()
    service_migrator = MigrationFacilitator(migrator_factory)
    service_migrator.service_manager = TestServiceManagerHandler()
    service_migrator.mongo_handler = TestMongoMigrator()
    service = TestMigratorPlugin()

    service_migrator.migrate([service], MigrationAction.RESTORE, "")

    assert service.restore_count == 1


@pytest.mark.unit
def test_capture_services_with_unknown_action_throws_exception():
    migrator_factory = MigratorFactory()
    service_migrator = MigrationFacilitator(migrator_factory)
    service_migrator.service_manager = TestServiceManagerHandler()
    service_migrator.mongo_handler = TestMongoMigrator()
    service = TestMigratorPlugin()

    with pytest.raises(ValueError):
        service_migrator.migrate([service], "unknown", "")


class TestMigratorPlugin(ServicePlugin):
    capture_count = 0
    restore_count = 0

    @property
    def help(self):
        return ""

    @property
    def names(self):
        return "test"

    def capture(self, mongo_handler=None, file_handler=None):
        self.capture_count += 1

    def restore(self, mongo_handler=None, file_handler=None):
        self.restore_count += 1


class TestServiceManagerHandler:
    are_services_running = True

    def stop_all_systemlink_services(self):
        self.are_services_running = False

    def start_all_systemlink_services(self):
        self.are_services_running = True


class TestMongoMigrator(MongoMigrator):
    is_mongo_running = True

    def start_mongo(self):
        self.is_mongo_running = True

    def stop_mongo(self):
        self.is_mongo_running = False
