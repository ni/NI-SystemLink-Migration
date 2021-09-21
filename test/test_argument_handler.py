import logging
from typing import List

import pytest

from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.argument_handler import CAPTURE_ARGUMENT
from nislmigrate.argument_handler import RESTORE_ARGUMENT
from nislmigrate.argument_handler import DEFAULT_MIGRATION_DIRECTORY
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, ArgumentManager
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.migration_action import MigrationAction
from nislmigrate.migrators.asset_migrator import AssetMigrator
from nislmigrate.migrators.tag_migrator import TagMigrator
from test.test_utilities import FakeFacadeFactory, FakeMigratorPluginLoader


@pytest.mark.unit
@pytest.mark.parametrize('arguments', [
    [],
    [CAPTURE_ARGUMENT, RESTORE_ARGUMENT],
    ['--tag'],
    [CAPTURE_ARGUMENT, '--invalid'],
    ['not_capture_or_restore'],
])
def test_invalid_arguments_exits_with_exception(arguments: List[str]):
    arguments = [CAPTURE_ARGUMENT, RESTORE_ARGUMENT]
    with pytest.raises(SystemExit):
        ArgumentHandler(arguments)


@pytest.mark.unit
def test_capture_tag_service_arguments_recognizes_capture_action():
    arguments = [CAPTURE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    migration_action = argument_handler.get_migration_action()

    assert migration_action == MigrationAction.CAPTURE


@pytest.mark.unit
def test_capture_tag_service_arguments_recognizes_tag_service():
    arguments = [CAPTURE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == TagMigrator().name


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_restore_action():
    arguments = [RESTORE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    migration_action = argument_handler.get_migration_action()

    assert migration_action == MigrationAction.RESTORE


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_tag_service():
    arguments = [RESTORE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == TagMigrator().name


@pytest.mark.unit
def test_restore_two_services_arguments_recognizes_both_services():
    arguments = [RESTORE_ARGUMENT, '--tags', '--assets']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 2
    first_service = services_to_migrate[0]
    second_service = services_to_migrate[1]
    assert first_service.name == TagMigrator().name or second_service.name == TagMigrator().name
    assert second_service.name == AssetMigrator().name or first_service.name == AssetMigrator().name


@pytest.mark.unit
def test_get_migration_directory_returns_default():
    arguments = [CAPTURE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    assert argument_handler.get_migration_directory() == DEFAULT_MIGRATION_DIRECTORY


@pytest.mark.unit
def test_get_migration_directory_returns_migration_directory():
    arguments = [CAPTURE_ARGUMENT, '--tags', '--dir=test']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    assert argument_handler.get_migration_directory() == 'test'


@pytest.mark.unit
def test_get_logging_verbosity_with_no_arguments():
    arguments = []
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    assert argument_handler.get_logging_verbosity() == logging.WARNING


@pytest.mark.unit
def test_is_force_migration_flag_present_short_flag_present():
    arguments = [RESTORE_ARGUMENT, '-f']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    assert argument_handler.is_force_migration_flag_present()


@pytest.mark.unit
def test_is_force_migration_flag_present_flag_not_present():
    arguments = [RESTORE_ARGUMENT]
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    assert not argument_handler.is_force_migration_flag_present()


@pytest.mark.unit
def test_is_force_migration_flag_present_flag_present():
    arguments = [RESTORE_ARGUMENT, '--force']
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    assert argument_handler.is_force_migration_flag_present()


@pytest.mark.unit
def test_is_force_migration_flag_present_during_capture_returns_false():
    arguments = [CAPTURE_ARGUMENT]
    argument_handler = ArgumentHandler(arguments, facade_factory=FakeFacadeFactory())

    assert not argument_handler.is_force_migration_flag_present()


@pytest.mark.unit
def test_migrator_with_no_additional_arguments_has_empty_additional_parameters():
    migrator = FakeMigrator(add_argument=False)
    loader = FakeMigratorPluginLoader([migrator])
    arguments = ['capture', '--fake']
    argument_handler = ArgumentHandler(
        arguments,
        facade_factory=FakeFacadeFactory(),
        plugin_loader=loader
    )

    result = argument_handler.get_list_of_services_to_capture_or_restore()

    assert result == [migrator]


@pytest.mark.unit
def test_migrator_with_additional_arguments_has_empty_additional_parameters_when_not_passed():
    migrator = FakeMigrator(add_argument=True)
    loader = FakeMigratorPluginLoader([migrator])
    arguments = ['capture', '--fake']
    argument_handler = ArgumentHandler(
        arguments,
        facade_factory=FakeFacadeFactory(),
        plugin_loader=loader
    )

    additional_arguments = argument_handler.get_migrator_additional_arguments(migrator)

    assert additional_arguments == {}


@pytest.mark.unit
def test_migrator_with_additional_arguments_has_additional_parameters_when_passed():
    migrator = FakeMigrator(add_argument=True)
    loader = FakeMigratorPluginLoader([migrator])
    arguments = ['capture', '--fake', '--fake-extra']
    argument_handler = ArgumentHandler(
        arguments,
        facade_factory=FakeFacadeFactory(),
        plugin_loader=loader
    )

    additional_arguments = argument_handler.get_migrator_additional_arguments(migrator)

    assert additional_arguments == {'extra': True}


@pytest.mark.unit
def test_migrator_with_additional_arguments_only_receives_own_arguments():
    migrator1 = FakeMigrator('one', 'mine', True)
    migrator2 = FakeMigrator('two', 'yours', True)
    loader = FakeMigratorPluginLoader([migrator1, migrator2])
    arguments = ['capture', '--one', '--one-mine', '--two', '--two-yours']
    argument_handler = ArgumentHandler(
        arguments,
        facade_factory=FakeFacadeFactory(),
        plugin_loader=loader
    )

    additional_arguments1 = argument_handler.get_migrator_additional_arguments(migrator1)
    additional_arguments2 = argument_handler.get_migrator_additional_arguments(migrator2)

    assert additional_arguments1 == {'mine': True}
    assert additional_arguments2 == {'yours': True}


@pytest.mark.unit
@pytest.mark.parametrize('operation', [
    'capture',
    'restore'
])
def test_service_not_installed_throws_migration_error(operation: str):
    migrator1 = FakeMigrator('one', 'mine', True)
    migrator2 = FakeMigrator('two', 'yours', True)
    loader = FakeMigratorPluginLoader([migrator1, migrator2])
    facade_factory = FakeFacadeFactory()
    facade_factory.file_system_facade.missing_files.append('one.json')
    arguments = [operation, '--one', '--one-mine', '--two', '--two-yours']
    argument_handler = ArgumentHandler(
        arguments,
        facade_factory=facade_factory,
        plugin_loader=loader
    )

    with pytest.raises(MigrationError):
        argument_handler.get_list_of_services_to_capture_or_restore()


class FakeMigrator(MigratorPlugin):
    def __init__(self, name: str = 'Fake', extra_argument_name: str = 'extra', add_argument: bool = False):
        self._add_argument = add_argument
        self._name = name
        self._extra_argument_name = extra_argument_name

    @property
    def argument(self) -> str:
        return self._name.lower()

    @property
    def name(self) -> str:
        return self._name

    @property
    def help(self) -> str:
        return f'{self._name} help'

    def capture(self, migration_directory, facade_factory, arguments) -> None:
        pass

    def restore(self, migration_directory, facade_factory, arguments) -> None:
        pass

    def pre_restore_check(self, migration_directory, facade_factory, arguments) -> None:
        pass

    def add_additional_arguments(self, argument_manager: ArgumentManager):
        if self._add_argument:
            argument_manager.add_switch(self._extra_argument_name, f'{self._extra_argument_name} help')
