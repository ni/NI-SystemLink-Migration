from nislmigrate.facades.process_facade import ProcessError
from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, ArgumentManager
from nislmigrate.migration_tool import run_migration_tool
import os
from pathlib import Path
import pytest
from test.test_utilities import FakeFacadeFactory, FakeMigratorPluginLoader, FakeMongoFacade, FakeProcessFacade
from typing import Any, Dict


@pytest.mark.unit
def test_run_migration_tool(tmp_path: Path) -> None:
    facade_factory = FakeFacadeFactory()
    migrator = configure_test_migrator(tmp_path, facade_factory)
    plugin_loader = FakeMigratorPluginLoader([migrator])
    migration_directory = str(tmp_path / 'data')

    capture_arguments = ['capture', '--test-migrator', '--dir', migration_directory]
    capture_argument_handler = ArgumentHandler(capture_arguments, plugin_loader)
    run_migration_tool(facade_factory, capture_argument_handler)
    assert facade_factory.process_facade.captured
    expected_output_path = os.path.join(migration_directory, migrator.name, migrator.name)
    assert os.path.isfile(expected_output_path)

    restore_arguments = ['restore', '--test-migrator', '--dir', migration_directory, '--force']
    restore_argument_handler = ArgumentHandler(restore_arguments, plugin_loader)
    facade_factory.process_facade.reset()
    run_migration_tool(facade_factory, restore_argument_handler)
    assert facade_factory.process_facade.restored
    assert Path(expected_output_path) == facade_factory.process_facade.last_restore_path


@pytest.mark.unit
def test_migrator_receives_extra_arguments(tmp_path) -> None:
    facade_factory = FakeFacadeFactory()
    migrator = configure_test_migrator(tmp_path, facade_factory)
    plugin_loader = FakeMigratorPluginLoader([migrator])
    migration_directory = str(tmp_path / 'data')
    expected_arguments = {'extra': True}

    capture_arguments = ['capture', '--test-migrator', '--test-migrator-extra', '--dir', migration_directory]
    capture_argument_handler = ArgumentHandler(capture_arguments, plugin_loader)
    run_migration_tool(facade_factory, capture_argument_handler)
    assert facade_factory.process_facade.captured

    restore_arguments = ['restore', '--test-migrator', '--test-migrator-extra', '--dir', migration_directory, '--force']
    restore_argument_handler = ArgumentHandler(restore_arguments, plugin_loader)
    facade_factory.process_facade.reset()
    run_migration_tool(facade_factory, restore_argument_handler)
    assert migrator.pre_restore_extra_arguments == expected_arguments
    assert migrator.restore_extra_arguments == expected_arguments


class FakeProcessFacadeWithPathVerification(FakeProcessFacade):
    def handle_mongo_dump(self, archive_path: Path):
        # create an empty file at the requested path
        archive_path.touch()

    def handle_mongo_restore(self, archive_path: Path):
        # ensure the requested file exists
        if not archive_path.exists():
            raise ProcessError('the archive does not exist')


class TestMigrator(MigratorPlugin):
    def __init__(self):
        self.catpure_extra_arguments = None
        self.restore_extra_arguments = None
        self.pre_restore_extra_arguments = None

    @property
    def argument(self) -> str:
        return 'test-migrator'

    @property
    def name(self) -> str:
        return 'TestMigrator'

    @property
    def help(self) -> str:
        return ''

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))

        mongo_facade.capture_database_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)

        self.capture_extra_arguments = arguments

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]) -> None:
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))

        mongo_facade.restore_database_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)

        self.restore_extra_arguments = arguments

    def pre_restore_check(
            self,
            migration_directory: str,
            facade_factory: FacadeFactory,
            arguments: Dict[str, Any]) -> None:
        self.pre_restore_extra_arguments = arguments

    def add_additional_arguments(self, argument_manager: ArgumentManager):
        argument_manager.add_switch('extra', 'extra help')


def configure_test_migrator(tmp_path: Path, facade_factory: FakeFacadeFactory) -> TestMigrator:
    config_directory = tmp_path / 'config'
    migrator = TestMigrator()
    migrator.service_configuration_directory = str(config_directory)

    facade_factory.process_facade = FakeProcessFacadeWithPathVerification()
    facade_factory.mongo_facade = FakeMongoFacade(facade_factory.process_facade)
    facade_factory.file_system_facade.config = {
        migrator.name: {
            'Mongo.CustomConnectionString': 'mongodb://localhost:27017',
            'Mongo.Database': 'db'
        }
    }

    return migrator
