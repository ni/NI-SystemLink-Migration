"""Migration tests."""

import os
import shutil
import sys
from unittest.mock import patch

import pytest

import slmigrate.argument_handler as arg_handler
import slmigrate.constants as constants
import slmigrate.filehandler as file_handler
from slmigrate.migrationaction import MigrationAction
from test import test_constants
from .context import systemlinkmigrate


@pytest.mark.unit
def test_double_action_args():
    """
    Given:
    """
    parser = arg_handler.create_nislmigrate_argument_parser()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parser.parse_args([constants.CAPTURE_ARG, constants.RESTORE_ARG])
        assert pytest_wrapped_e.type == SystemExit


@pytest.mark.unit
def test_no_action_args():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.create_nislmigrate_argument_parser()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parser.parse_args(["--" + constants.tag.arg])
    assert pytest_wrapped_e.type == SystemExit


@pytest.mark.unit
def test_capture_tag_service_arguments_recognizes_capture_action():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.create_nislmigrate_argument_parser()
    arguments = parser.parse_args([constants.CAPTURE_ARG, "--" + constants.tag.arg])

    migration_action = arg_handler.determine_migration_action(arguments)

    assert migration_action == MigrationAction.CAPTURE


@pytest.mark.unit
def test_capture_tag_service_arguments_recognizes_tag_service():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.create_nislmigrate_argument_parser()
    arguments = parser.parse_args([constants.CAPTURE_ARG, "--" + constants.tag.arg])
    services_to_migrate = arg_handler.get_list_of_services_to_capture_or_restore(arguments)

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == constants.tag.arg


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_restore_action():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.create_nislmigrate_argument_parser()
    arguments = parser.parse_args([constants.RESTORE_ARG, "--" + constants.tag.arg])

    migration_action = arg_handler.determine_migration_action(arguments)

    assert migration_action == MigrationAction.RESTORE


@pytest.mark.unit
def test_restore_tag_service_arguments_recognizes_tag_service():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.create_nislmigrate_argument_parser()
    arguments = parser.parse_args([constants.RESTORE_ARG, "--" + constants.tag.arg])

    services_to_migrate = arg_handler.get_list_of_services_to_capture_or_restore(arguments)

    assert len(services_to_migrate) == 1
    assert services_to_migrate[0].name == constants.tag.arg


# TODO: Replace this with a true unit test and move this to an integration test.
# def test_capture_migrate_mongo_data():
#     """TODO: Complete documentation.
#
#     :return:
#     """
#     constants.mongo_config = test_constants.mongo_config
#     constants.mongo_dump = test_constants.mongo_dump
#     constants.mongo_restore = test_constants.mongo_restore
#     constants.migration_dir = test_constants.migration_dir
#     constants.service_config_dir = test_constants.service_config_dir
#     mongo_process = mongo_handler.start_mongo(
#         test_constants.mongod_exe, test_constants.mongo_config
#     )
#     test_service = test_constants.test_service
#     if os.path.isdir(constants.migration_dir):
#         shutil.rmtree(constants.migration_dir)
#     config = mongo_handler.get_service_config(test_service)
#     mongo_handler.migrate_mongo_cmd(test_service, constants.CAPTURE_ARG, config)
#     dump_dir = os.path.join(constants.migration_dir, "local")
#     mongo_handler.stop_mongo(mongo_process)
#     files = os.walk(dump_dir)
#     for file in files:
#         assert str(file).endswith(".bzon.gz, .json.gz")


@pytest.mark.unit
def test_capture_migrate_dir():
    """TODO: Complete documentation.

    :return:
    """
    test_service = test_constants.test_service
    if os.path.isdir(test_service.migration_dir):
        shutil.rmtree(test_service.migration_dir)
    if os.path.isdir(test_service.source_dir):
        shutil.rmtree(test_service.source_dir)
    os.makedirs(test_service.source_dir)
    os.makedirs(os.path.join(test_service.source_dir, "lev1"))
    os.makedirs(os.path.join(test_service.source_dir, "lev1", "lev2"))
    file_handler.migrate_dir(constants.default_migration_dir, test_service, constants.CAPTURE_ARG)
    assert os.path.isdir(os.path.join(constants.default_migration_dir, test_service.name, "lev1", "lev2"))
    shutil.rmtree(test_service.source_dir)
    shutil.rmtree(constants.default_migration_dir)


@pytest.mark.unit
def test_capture_migrate_singlefile():
    """TODO: Complete documentation.

    :return:
    """
    test = test_constants.test_service
    if os.path.isdir(test.singlefile_migration_dir):
        shutil.rmtree(test.singlefile_migration_dir)
    if os.path.isdir(test.singlefile_source_dir):
        shutil.rmtree(test.singlefile_source_dir)
    os.makedirs(test.singlefile_source_dir)
    os.makedirs(test.singlefile_migration_dir)
    test_file = open(os.path.join(test.singlefile_source_dir, "demofile2.txt"), "a")
    test_file.close()
    file_handler.migrate_singlefile(test.singlefile_migration_dir, test, constants.CAPTURE_ARG)
    assert os.path.isfile(os.path.join(test.migration_dir, "demofile2.txt"))
    shutil.rmtree(test.singlefile_source_dir)
    shutil.rmtree(test.singlefile_migration_dir)


@pytest.mark.unit
def test_missing_migration_directory():
    """TODO: Complete documentation.

    :return:
    """
    test_args = [
        test_constants.MIGRATION_CMD,
        constants.RESTORE_ARG,
        "--" + constants.tag.arg,
        "--" + constants.MIGRATION_ARG,
        test_constants.migration_dir,
    ]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0


@pytest.mark.unit
def test_missing_service_migration_file():
    """TODO: Complete documentation.

    :return:
    """
    test_args = [
        test_constants.MIGRATION_CMD,
        constants.RESTORE_ARG,
        "--" + constants.tag.arg,
        "--" + constants.MIGRATION_ARG,
        test_constants.migration_dir,
    ]
    os.makedirs(constants.default_migration_dir)
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0
    shutil.rmtree(constants.default_migration_dir)


@pytest.mark.unit
def test_missing_service_migration_dir():
    """TODO: Complete documentation.

    :return:
    """
    test_args = [
        test_constants.MIGRATION_CMD,
        constants.RESTORE_ARG,
        "--" + constants.fis.arg,
        "--" + constants.MIGRATION_ARG,
        test_constants.migration_dir,
    ]
    os.makedirs(constants.default_migration_dir)
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0
    shutil.rmtree(constants.default_migration_dir)
