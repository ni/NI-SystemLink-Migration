import os
from unittest.mock import patch, Mock

import pytest as pytest
from testfixtures import tempdir, TempDirectory

from nislmigrate.facades import mongo_configuration
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade


@pytest.mark.unit
@tempdir()
@patch('subprocess.run')
def test_mongo_facade_capture_migration_directory_created_when_it_does_not_exist(
        run: Mock,
        temp_directory: TempDirectory,
) -> None:
    migration_directory = os.path.join(temp_directory.path, "migration")
    assert not os.path.exists(migration_directory)
    configuration = FakeMongoConfiguration()
    mongo_facade = MongoFacade()

    mongo_facade.capture_database_to_directory(configuration, migration_directory, "testname.gz")

    assert os.path.exists(migration_directory)
    run.verify_called()


@pytest.mark.unit
@tempdir()
@patch('subprocess.run')
def test_mongo_facade_capture_migration_directory_already_exists_and_empty(
        run: Mock,
        temp_directory: TempDirectory,
) -> None:
    migration_directory = make_directory(temp_directory, "migration")
    assert os.path.exists(migration_directory)
    configuration = FakeMongoConfiguration()
    mongo_facade = MongoFacade()

    mongo_facade.capture_database_to_directory(configuration, migration_directory, "testname.gz")

    assert os.path.exists(migration_directory)
    run.verify_called()


def make_directory(temp_directory: TempDirectory, name: str) -> str:
    path = os.path.join(temp_directory.path, name)
    os.mkdir(path)
    return path


class FakeMongoConfiguration(MongoConfiguration):
    def __init__(self):
        super().__init__({
            mongo_configuration.MONGO_PASSWORD_CONFIGURATION_KEY: "",
            mongo_configuration.MONGO_USER_CONFIGURATION_KEY: "",
            mongo_configuration.MONGO_CUSTOM_CONNECTION_STRING_CONFIGURATION_KEY: "",
            mongo_configuration.MONGO_PORT_NAME_CONFIGURATION_KEY: "",
            mongo_configuration.MONGO_DATABASE_NAME_CONFIGURATION_KEY: "",
            mongo_configuration.MONGO_HOST_NAME_CONFIGURATION_KEY: "",
        })
