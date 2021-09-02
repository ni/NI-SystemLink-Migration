import os
from unittest.mock import patch, Mock

import pytest as pytest
from testfixtures import tempdir, TempDirectory

from nislmigrate.facades import mongo_configuration
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.process_facade import ProcessFacade


@pytest.mark.unit
@tempdir()
@patch('subprocess.run')
@patch('subprocess.Popen')
def test_mongo_facade_capture_migration_directory_created_when_it_does_not_exist(
        process_open: Mock,
        run: Mock,
        temp_directory: TempDirectory,
) -> None:
    migration_directory = os.path.join(temp_directory.path, "migration")
    assert not os.path.exists(migration_directory)
    configuration = get_fake_mongo_configuration()
    mongo_facade = MongoFacade(ProcessFacade())

    mongo_facade.capture_database_to_directory(configuration, migration_directory, "testname.gz")

    assert os.path.exists(migration_directory)
    run.assert_called()
    process_open.assert_called()


@pytest.mark.unit
@tempdir()
@patch('subprocess.run')
@patch('subprocess.Popen')
def test_mongo_facade_capture_migration_nested_directory_created_when_it_does_not_exist(
        process_open: Mock,
        run: Mock,
        temp_directory: TempDirectory,
) -> None:
    migration_directory = os.path.join(temp_directory.path, "migration", "other")
    assert not os.path.exists(migration_directory)
    configuration = get_fake_mongo_configuration()
    mongo_facade = MongoFacade(ProcessFacade())

    mongo_facade.capture_database_to_directory(configuration, migration_directory, "testname.gz")

    assert os.path.exists(migration_directory)
    run.assert_called()
    process_open.assert_called()


@pytest.mark.unit
@tempdir()
@patch('subprocess.run')
@patch('subprocess.Popen')
def test_mongo_facade_capture_migration_directory_already_exists_and_empty(
        process_open: Mock,
        run: Mock,
        temp_directory: TempDirectory,
) -> None:
    migration_directory = make_directory(temp_directory, "migration")
    assert os.path.exists(migration_directory)
    configuration = get_fake_mongo_configuration()
    mongo_facade = MongoFacade(ProcessFacade())

    mongo_facade.capture_database_to_directory(configuration, migration_directory, "testname.gz")

    assert os.path.exists(migration_directory)
    run.assert_called()
    process_open.assert_called()


def make_directory(temp_directory: TempDirectory, name: str) -> str:
    path = os.path.join(temp_directory.path, name)
    os.mkdir(path)
    return path


def get_fake_mongo_configuration():
    return MongoConfiguration({
        mongo_configuration.MONGO_PASSWORD_CONFIGURATION_KEY: "",
        mongo_configuration.MONGO_USER_CONFIGURATION_KEY: "",
        mongo_configuration.MONGO_CUSTOM_CONNECTION_STRING_CONFIGURATION_KEY: "",
        mongo_configuration.MONGO_PORT_NAME_CONFIGURATION_KEY: "",
        mongo_configuration.MONGO_DATABASE_NAME_CONFIGURATION_KEY: "",
        mongo_configuration.MONGO_HOST_NAME_CONFIGURATION_KEY: "",
    })
