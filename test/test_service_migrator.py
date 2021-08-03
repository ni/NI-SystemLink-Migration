import slmigrate.argument_handler as arg_handler
import slmigrate.constants as constants
import slmigrate.filehandler as file_handler
from slmigrate.migrationaction import MigrationAction
from slmigrate.mongohandler import MongoHandler
from slmigrate.service import ServicePlugin
from slmigrate.servicemigrator import ServiceMigrator
from .context import systemlinkmigrate
import pytest

@pytest.mark.unit
def test_capture_services_with_restore_action_captures_plugin():
    service_migrator = ServiceMigrator()
    service_migrator.service_manager = TestServiceManagerHandler()
    service_migrator.mongo_handler = TestMongoHandler()
    service = TestMigratorPlugin()

    service_migrator.migrate_services([service], MigrationAction.CAPTURE, "")

    assert service.capture_count == 1

@pytest.mark.unit
def test_capture_services_with_restore_action_restores_plugin():
    service_migrator = ServiceMigrator()
    service_migrator.service_manager = TestServiceManagerHandler()
    service_migrator.mongo_handler = TestMongoHandler()
    service = TestMigratorPlugin()

    service_migrator.migrate_services([service], MigrationAction.RESTORE, "")

    assert service.restore_count == 1

@pytest.mark.unit
def test_capture_services_with_unknown_action_throws_exception():
    service_migrator = ServiceMigrator()
    service_migrator.service_manager = TestServiceManagerHandler()
    service_migrator.mongo_handler = TestMongoHandler()
    service = TestMigratorPlugin()

    with pytest.raises(ValueError):
        service_migrator.migrate_services([service], "unknown", "")


class TestMigratorPlugin(ServicePlugin):
    capture_count = 0;
    restore_count = 0;

    @property
    def help(self):
        return ""

    @property
    def names(self):
        return "test"

    def capture(self, args, mongohandler=None, filehandler=None):
        self.capture_count += 1

    def restore(self, args, mongohandler=None, filehandler=None):
        self.restore_count += 1

class TestServiceManagerHandler:
    are_services_running = True

    def stop_all_sl_services(self):
        self.are_services_running = False

    def start_all_sl_services(self):
        self.are_services_running = True
0
class TestMongoHandler(MongoHandler):
    is_mongo_running = True

    def start_mongo(self):
        self.is_mongo_running = True

    def stop_mongo(self):
        self.is_mongo_running = False