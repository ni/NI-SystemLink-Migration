import json
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.process_facade import ProcessFacade, BackgroundProcess, ProcessError
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.migration_action import MigrationAction
from nislmigrate.migration_tool import run_migration_tool
from pathlib import Path
import pytest
from test.test_utilities import FakeServiceManager, NoopBackgroundProcess
from typing import Any, Dict, List


@pytest.mark.unit
def test_run_migration_tool(tmp_path: Path) -> None:
    migrator = configure_test_migrator(tmp_path)
    services_to_migrate: List[MigratorPlugin] = [migrator]

    facade_factory = FacadeFactory()
    mongo_facade = facade_factory.get_mongo_facade()
    process_facade = FakeProcessFacade()
    mongo_facade.process_facade = process_facade
    facade_factory.system_link_service_manager_facade = FakeServiceManager()
    migration_directory = str(tmp_path / 'data')

    run_migration_tool(facade_factory, services_to_migrate, MigrationAction.CAPTURE, migration_directory)
    assert process_facade.captured

    process_facade.reset()
    run_migration_tool(facade_factory, services_to_migrate, MigrationAction.RESTORE, migration_directory)
    assert process_facade.restored


class FakeProcessFacade(ProcessFacade):
    def __init__(self):
        self.reset()

    def reset(self):
        self.captured: bool = False
        self.restored: bool = False

    def run_process(self, args: List[str]):
        archive_arg = [a for a in args if a.startswith('--archive=')][0]
        if not archive_arg:
            raise ProcessError('missing --archive= argument')

        archive = Path(archive_arg.split('=')[1])

        if 'mongodump' in args[0]:
            archive.touch()
            self.captured = True
        elif 'mongorestore' in args[0]:
            if not archive.exists():
                raise ProcessError('the archive does not exist')
            self.restored = True
        else:
            raise ProcessError('unknown command')

    def run_background_process(self, args: List[str]) -> BackgroundProcess:
        return NoopBackgroundProcess(args)


class TestMigrator(MigratorPlugin):
    @property
    def argument(self) -> str:
        return "test-migrator"

    @property
    def name(self) -> str:
        return "TestMigrator"

    @property
    def help(self) -> str:
        return ""

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        pass


def configure_test_migrator(tmp_path: Path) -> TestMigrator:
    config_directory = tmp_path / 'config'
    migrator = TestMigrator()
    migrator.service_configuration_directory = str(config_directory)

    configuration = {
        migrator.name: {
            "Mongo.CustomConnectionString": "mongodb://localhost:27017",
            "Mongo.Database": "db"
        }
    }
    config_directory.mkdir()
    with open(config_directory / f'{migrator.name}.json', "w", encoding="utf-8-sig") as f:
        f.write(json.dumps(configuration))

    return migrator
