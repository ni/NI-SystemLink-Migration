"""Migration tests."""

import os
import shutil
import sys
from unittest.mock import patch

import pytest

import slmigrate.constants as constants
import slmigrate.filehandler as file_handler
from test import test_constants
from .context import systemlinkmigrate


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
    file_handler.migrate_dir(constants.DEFAULT_MIGRATION_DIRECTORY, test_service, constants.CAPTURE_ARGUMENT)
    assert os.path.isdir(os.path.join(constants.DEFAULT_MIGRATION_DIRECTORY, test_service.name, "lev1", "lev2"))
    shutil.rmtree(test_service.source_dir)
    shutil.rmtree(constants.DEFAULT_MIGRATION_DIRECTORY)


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
    file_handler.migrate_singlefile(test.singlefile_migration_dir, test, constants.CAPTURE_ARGUMENT)
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
        constants.RESTORE_ARGUMENT,
        "--" + constants.tag.arg,
        "--" + constants.MIGRATION_DIRECTORY_ARGUMENT,
        test_constants.migration_dir,
    ]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(FileNotFoundError):
            systemlinkmigrate.main_without_admin_check()


@pytest.mark.unit
def test_missing_service_migration_file():
    """TODO: Complete documentation.

    :return:
    """
    test_args = [
        test_constants.MIGRATION_CMD,
        constants.RESTORE_ARGUMENT,
        "--" + constants.tag.arg,
        "--" + constants.MIGRATION_DIRECTORY_ARGUMENT,
        test_constants.migration_dir,
    ]
    os.makedirs(constants.DEFAULT_MIGRATION_DIRECTORY)
    with patch.object(sys, "argv", test_args):
        with pytest.raises(FileNotFoundError):
            systemlinkmigrate.main_without_admin_check()
    shutil.rmtree(constants.DEFAULT_MIGRATION_DIRECTORY)


@pytest.mark.unit
def test_missing_service_migration_dir():
    """TODO: Complete documentation.

    :return:
    """
    test_args = [
        test_constants.MIGRATION_CMD,
        constants.RESTORE_ARGUMENT,
        "--" + constants.fis.arg,
        "--" + constants.MIGRATION_DIRECTORY_ARGUMENT,
        test_constants.migration_dir,
    ]
    os.makedirs(constants.DEFAULT_MIGRATION_DIRECTORY)
    with patch.object(sys, "argv", test_args):
        with pytest.raises(FileNotFoundError):
            systemlinkmigrate.main_without_admin_check()
    shutil.rmtree(constants.DEFAULT_MIGRATION_DIRECTORY)
