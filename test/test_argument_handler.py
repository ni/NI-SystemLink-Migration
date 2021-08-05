import os
import shutil
import sys
from unittest.mock import patch

import pytest

from slmigrate.argument_handler import ArgumentHandler
import slmigrate.constants as constants
from slmigrate.migrationaction import MigrationAction


@pytest.mark.unit
@pytest.mark.parametrize("arguments", [
    [],
    [constants.CAPTURE_ARGUMENT, constants.RESTORE_ARGUMENT],
    ["--" + constants.tag.arg],
    [constants.CAPTURE_ARGUMENT, "--invalid"],
    ["notcaptureorrestore"],
])
def test_invalid_arguments_exits_with_exception(arguments):
    """
    Given:
    """
    arguments = [constants.CAPTURE_ARGUMENT, constants.RESTORE_ARGUMENT]
    with pytest.raises(SystemExit):
        ArgumentHandler(arguments)


@pytest.mark.unit
def test_capture_tag_service_arguments_recognizes_capture_action():
    """TODO: Complete documentation.

    :return:
    """
    arguments = [constants.CAPTURE_ARGUMENT, "--" + constants.tag.arg]
    argument_handler = ArgumentHandler(arguments)

    migration_action = argument_handler.determine_migration_action()

    assert migration_action == MigrationAction.CAPTURE


@pytest.mark.unit
def test_capture_tag_service_arguments_recognizes_tag_service():
    """TODO: Complete documentation.

    :return:
    """
    arguments = [constants.CAPTURE_ARGUMENT, "--" + constants.tag.arg]
    argument_handler = ArgumentHandler(arguments)

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == constants.tag.arg


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_restore_action():
    """TODO: Complete documentation.

    :return:
    """
    arguments = [constants.RESTORE_ARGUMENT, "--" + constants.tag.arg]
    argument_handler = ArgumentHandler(arguments)

    migration_action = argument_handler.determine_migration_action()

    assert migration_action == MigrationAction.RESTORE


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_tag_service():
    """TODO: Complete documentation.

    :return:
    """
    arguments = [constants.RESTORE_ARGUMENT, "--" + constants.tag.arg]
    argument_handler = ArgumentHandler(arguments)

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == constants.tag.arg


@pytest.mark.unit
def test_restore_two_services_arguments_recognizes_both_services():
    """TODO: Complete documentation.

    :return:
    """
    arguments = [constants.RESTORE_ARGUMENT, "--" + constants.tag.arg, "--" + constants.asset.arg]
    argument_handler = ArgumentHandler(arguments)

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()

    assert len(services_to_migrate) == 2
    assert services_to_migrate[0].name == constants.tag.arg or services_to_migrate[1].name == constants.tag.arg
    assert services_to_migrate[1].name == constants.asset.arg or services_to_migrate[0].name == constants.asset.arg

@pytest.mark.unit
def test_parse_custom_directory():
    """TODO: Complete documentation.

    :return:
    """
    arguments = [constants.CAPTURE_ARGUMENT, "--" + constants.tag.arg, "--dir=test"]
    argument_handler = ArgumentHandler(arguments)

    assert argument_handler.get_migration_directory_from_arguments() == "test"
