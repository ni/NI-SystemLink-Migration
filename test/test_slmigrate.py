import pytest
import os
import sys
import shutil
from unittest.mock import patch
import slmigrate.constants as constants
import slmigrate.mongohandler as mongohandler
import slmigrate.arghandler as arghandler
import slmigrate.filehandler as filehandler
from .context import systemlinkmigrate
from test import test_constants


def test_parse_arguments():
    parser = arghandler.parse_arguments()
    assert parser.parse_args([constants.capture_arg,
                              "--" + constants.tag.arg,
                              "--" + constants.opc.arg,
                              "--" + constants.testmonitor.arg,
                              "--" + constants.alarmrule.arg,
                              "--" + constants.opc.arg,
                              "--" + constants.asset.arg,
                              "--" + constants.repository.arg,
                              "--" + constants.userdata.arg,
                              "--" + constants.notification.arg,
                              "--" + constants.states.arg])


def test_double_action_args():
    parser = arghandler.parse_arguments()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parser.parse_args([constants.capture_arg, constants.restore_arg])
    assert pytest_wrapped_e.type == SystemExit


def test_no_action_args():
    parser = arghandler.parse_arguments()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        parser.parse_args(["--" + constants.tag.arg])
    assert pytest_wrapped_e.type == SystemExit


def test_determine_migrate_action_capture():
    test_service_tuple = [(constants.tag, constants.capture_arg)]
    parser = arghandler.parse_arguments()
    arguments = parser.parse_args([constants.capture_arg, "--" + constants.tag.arg])
    services_to_migrate = arghandler.determine_migrate_action(arguments)
    assert services_to_migrate == test_service_tuple


def test_determine_migrate_action_restore():
    test_service_tuple = [(constants.opc, constants.restore_arg)]
    parser = arghandler.parse_arguments()
    arguments = parser.parse_args([constants.restore_arg, "--" + constants.opc.arg])
    services_to_migrate = arghandler.determine_migrate_action(arguments)
    assert services_to_migrate == test_service_tuple


def test_determine_migrate_action_thdbbg():
    test_service_tuple = [(constants.tag, constants.thdbbug.arg)]
    parser = arghandler.parse_arguments()
    arguments = parser.parse_args([constants.thdbbug.arg])
    services_to_migrate = arghandler.determine_migrate_action(arguments)
    assert services_to_migrate == test_service_tuple


def test_capture_migrate_mongo_data():
    constants.mongo_config = test_constants.mongo_config
    constants.mongo_dump = test_constants.mongo_dump
    constants.mongo_restore = test_constants.mongo_restore
    constants.migration_dir = test_constants.migration_dir
    constants.service_config_dir = test_constants.service_config_dir
    mongo_process = mongohandler.start_mongo(test_constants.mongod_exe, test_constants.mongo_config)
    test_service = test_constants.test_service
    if os.path.isdir(constants.migration_dir):
        shutil.rmtree(constants.migration_dir)
    config = mongohandler.get_service_config(test_service)
    mongohandler.migrate_mongo_cmd(test_service, constants.capture_arg, config)
    dump_dir = os.path.join(constants.migration_dir, "local")
    mongohandler.stop_mongo(mongo_process)
    files = os.walk(dump_dir)
    for file in files:
        assert str(file).endswith((".bzon.gz, .json.gz"))


def check_migration_dir():
    test_dir = os.mkdir(os.path.join(os.path.abspath(os.sep)), "test_dir")
    filehandler.check_migration_dir(test_dir)
    assert not os.path.isdir(test_dir)


def test_capture_migrate_dir():
    test = test_constants.test_service
    constants.migration_dir = test_constants.migration_dir
    if os.path.isdir(test.MIGRATION_DIR):
        shutil.rmtree(test.MIGRATION_DIR)
    if os.path.isdir(test.source_dir):
        shutil.rmtree(test.source_dir)
    os.mkdir(test.source_dir)
    os.mkdir(os.path.join(test.source_dir, "lev1"))
    os.mkdir(os.path.join(test.source_dir, "lev1", "lev2"))
    filehandler.migrate_dir(test, constants.capture_arg)
    assert os.path.isdir(os.path.join(constants.migration_dir, test.name, "lev1", "lev2"))
    shutil.rmtree(test.source_dir)
    shutil.rmtree(constants.migration_dir)


def test_capture_migrate_singlefile():
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
    filehandler.migrate_singlefile(test, constants.capture_arg)
    assert os.path.isfile(os.path.join(test.MIGRATION_DIR, "demofile2.txt"))
    shutil.rmtree(test.source_dir)
    shutil.rmtree(constants.migration_dir)


def test_missing_migration_directory():
    test_args = [test_constants.migration_cmd, constants.restore_arg, "--" + constants.tag.arg, "--" + constants.migration_arg, test_constants.migration_dir]
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0


def test_missing_service_migration_file():
    test_args = [test_constants.migration_cmd, constants.restore_arg, "--" + constants.tag.arg, "--" + constants.migration_arg, test_constants.migration_dir]
    os.mkdir(constants.migration_dir)
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0
    shutil.rmtree(constants.migration_dir)


def test_missing_service_migration_dir():
    test_args = [test_constants.migration_cmd, constants.restore_arg, "--" + constants.fis.arg, "--" + constants.migration_arg, test_constants.migration_dir]
    os.mkdir(constants.migration_dir)
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            systemlinkmigrate.main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code != 0
    shutil.rmtree(constants.migration_dir)

