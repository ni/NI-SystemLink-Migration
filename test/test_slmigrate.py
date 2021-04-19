"""Migration tests."""

import os
import shutil
import sys
from unittest.mock import patch

import pytest

import slmigrate.arghandler as arg_handler
import slmigrate.constants as constants
import slmigrate.filehandler as file_handler
import slmigrate.mongohandler as mongo_handler
from test import test_constants
from .context import systemlinkmigrate


def test_parse_arguments():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.parse_arguments()
    assert parser.parse_args(
        [
            constants.CAPTURE_ARG,
            "--" + constants.tag.arg,
            "--" + constants.opc.arg,
            "--" + constants.testmonitor.arg,
            "--" + constants.alarmrule.arg,
            "--" + constants.opc.arg,
            "--" + constants.asset.arg,
            "--" + constants.repository.arg,
            "--" + constants.userdata.arg,
            "--" + constants.notification.arg,
            "--" + constants.states.arg,
        ]
    )


def test_double_action_args():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.parse_arguments()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parser.parse_args([constants.CAPTURE_ARG, constants.RESTORE_ARG])
    assert pytest_wrapped_e.type == SystemExit


def test_no_action_args():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.parse_arguments()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parser.parse_args(["--" + constants.tag.arg])
    assert pytest_wrapped_e.type == SystemExit


def test_determine_migrate_action_capture():
    """TODO: Complete documentation.

    :return:
    """
    test_service_tuple = [(constants.tag, constants.CAPTURE_ARG)]
    parser = arg_handler.parse_arguments()
    arguments = parser.parse_args([constants.CAPTURE_ARG, "--" + constants.tag.arg])
    services_to_migrate = arg_handler.determine_migrate_action(arguments)
    assert services_to_migrate == test_service_tuple


def test_determine_migrate_action_restore():
    """TODO: Complete documentation.

    :return:
    """
    test_service_tuple = [(constants.opc, constants.RESTORE_ARG)]
    parser = arg_handler.parse_arguments()
    arguments = parser.parse_args([constants.RESTORE_ARG, "--" + constants.opc.arg])
    services_to_migrate = arg_handler.determine_migrate_action(arguments)
    assert services_to_migrate == test_service_tuple


def test_determine_migrate_action_thdbbg():
    """TODO: Complete documentation.

    :return:
    """
    test_service_tuple = [(constants.tag, constants.thdbbug.arg)]
    parser = arg_handler.parse_arguments()
    arguments = parser.parse_args([constants.thdbbug.arg])
    services_to_migrate = arg_handler.determine_migrate_action(arguments)
    assert services_to_migrate == test_service_tuple


def test_capture_migrate_mongo_data():
    """TODO: Complete documentation.

    :return:
    """
    constants.mongo_config = test_constants.mongo_config
    constants.mongo_dump = test_constants.mongo_dump
    constants.mongo_restore = test_constants.mongo_restore
    constants.migration_dir = test_constants.migration_dir
    constants.service_config_dir = test_constants.service_config_dir
    mongo_process = mongo_handler.start_mongo(
        test_constants.mongod_exe, test_constants.mongo_config
    )
    test_service = test_constants.test_service
    if os.path.isdir(constants.migration_dir):
        shutil.rmtree(constants.migration_dir)
    config = mongo_handler.get_service_config(test_service)
    mongo_handler.migrate_mongo_cmd(test_service, constants.CAPTURE_ARG, config)
    dump_dir = os.path.join(constants.migration_dir, "local")
    mongo_handler.stop_mongo(mongo_process)
    files = os.walk(dump_dir)
    for file in files:
        assert str(file).endswith(".bzon.gz, .json.gz")


def test_capture_migrate_dir():
    """TODO: Complete documentation.

    :return:
    """
    test = test_constants.test_service
    constants.migration_dir = test_constants.migration_dir
    if os.path.isdir(test.migration_dir):
        shutil.rmtree(test.migration_dir)
    if os.path.isdir(test.source_dir):
        shutil.rmtree(test.source_dir)
    os.mkdir(test.source_dir)
    os.mkdir(os.path.join(test.source_dir, "lev1"))
    os.mkdir(os.path.join(test.source_dir, "lev1", "lev2"))
    file_handler.migrate_dir(test, constants.CAPTURE_ARG)
    assert os.path.isdir(os.path.join(constants.migration_dir, test.name, "lev1", "lev2"))
    shutil.rmtree(test.source_dir)
    shutil.rmtree(constants.migration_dir)


def test_capture_migrate_singlefile():
    """TODO: Complete documentation.

    :return:
    """
    constants.migration_dir = test_constants.migration_dir
    test = test_constants.test_service
    if os.path.isdir(test.singlefile_migration_dir):
        shutil.rmtree(test.singlefile_migration_dir)
    if os.path.isdir(test.singlefile_source_dir):
        shutil.rmtree(test.singlefile_source_dir)
    os.mkdir(test.singlefile_source_dir)
    os.mkdir(constants.migration_dir)
    test_file = open(os.path.join(test.singlefile_source_dir, "demofile2.txt"), "a")
    test_file.close()
    file_handler.migrate_singlefile(test, constants.CAPTURE_ARG)
    assert os.path.isfile(os.path.join(test.migration_dir, "demofile2.txt"))
    shutil.rmtree(test.source_dir)
    shutil.rmtree(constants.migration_dir)


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
    os.mkdir(constants.migration_dir)
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0
    shutil.rmtree(constants.migration_dir)


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
    os.mkdir(constants.migration_dir)
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0
    shutil.rmtree(constants.migration_dir)
