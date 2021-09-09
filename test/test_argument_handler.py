import logging
from typing import List

import pytest

from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.argument_handler import CAPTURE_ARGUMENT
from nislmigrate.argument_handler import RESTORE_ARGUMENT
from nislmigrate.argument_handler import DEFAULT_MIGRATION_DIRECTORY

from nislmigrate.migration_action import MigrationAction
from nislmigrate.migrators.asset_migrator import AssetMigrator
from nislmigrate.migrators.tag_migrator import TagMigrator


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
    argument_handler = ArgumentHandler(arguments)

    migration_action = argument_handler.get_migration_action()

    assert migration_action == MigrationAction.CAPTURE


@pytest.mark.unit
def test_capture_tag_service_arguments_recognizes_tag_service():
    arguments = [CAPTURE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments)

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == TagMigrator().name


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_restore_action():
    arguments = [RESTORE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments)

    migration_action = argument_handler.get_migration_action()

    assert migration_action == MigrationAction.RESTORE


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_tag_service():
    arguments = [RESTORE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments)

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == TagMigrator().name


@pytest.mark.unit
def test_restore_two_services_arguments_recognizes_both_services():
    arguments = [RESTORE_ARGUMENT, '--tags', '--assets']
    argument_handler = ArgumentHandler(arguments)

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 2
    first_service = services_to_migrate[0]
    second_service = services_to_migrate[1]
    assert first_service.name == TagMigrator().name or second_service.name == TagMigrator().name
    assert second_service.name == AssetMigrator().name or first_service.name == AssetMigrator().name


@pytest.mark.unit
def test_get_migration_directory_returns_default():
    arguments = [CAPTURE_ARGUMENT, '--tags']
    argument_handler = ArgumentHandler(arguments)

    assert argument_handler.get_migration_directory() == DEFAULT_MIGRATION_DIRECTORY


@pytest.mark.unit
def test_get_migration_directory_returns_migration_directory():
    arguments = [CAPTURE_ARGUMENT, '--tags', '--dir=test']
    argument_handler = ArgumentHandler(arguments)

    assert argument_handler.get_migration_directory() == 'test'


@pytest.mark.unit
def test_get_logging_verbosity_with_no_arguments():
    arguments = []
    argument_handler = ArgumentHandler(arguments)

    assert argument_handler.get_logging_verbosity() == logging.WARNING


@pytest.mark.unit
def test_is_force_migration_flag_present_short_flag_present():
    arguments = [RESTORE_ARGUMENT, '-f']
    argument_handler = ArgumentHandler(arguments)

    assert argument_handler.is_force_migration_flag_present()


@pytest.mark.unit
def test_is_force_migration_flag_present_flag_not_present():
    arguments = [RESTORE_ARGUMENT]
    argument_handler = ArgumentHandler(arguments)

    assert not argument_handler.is_force_migration_flag_present()


@pytest.mark.unit
def test_is_force_migration_flag_present_flag_present():
    arguments = [RESTORE_ARGUMENT, '--force']
    argument_handler = ArgumentHandler(arguments)

    assert argument_handler.is_force_migration_flag_present()


@pytest.mark.unit
def test_is_force_migration_flag_present_during_capture_returns_false():
    arguments = [CAPTURE_ARGUMENT]
    argument_handler = ArgumentHandler(arguments)

    assert not argument_handler.is_force_migration_flag_present()
