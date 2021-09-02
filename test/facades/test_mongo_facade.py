import os
from unittest.mock import patch, Mock

import pytest as pytest
from testfixtures import tempdir, TempDirectory

from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade

connection_string = "mongodb://127.17.0.5:27017/?gssapiServiceName=mongodb"


@pytest.mark.unit
@tempdir()
@patch('subprocess.run')
def test_mongo_facade_capture(run: Mock, temp_directory: TempDirectory) -> None:
    migration_directory = os.path.join(temp_directory.path, "migration")
    assert not os.path.exists(migration_directory)
    mongo_configuration = FakeMongoConfiguration()
    mongo_configuration.custom_connection_string = connection_string
    mongo_facade = MongoFacade()

    mongo_facade.capture_database_to_directory(mongo_configuration, migration_directory, "testname.gz")

    assert os.path.exists(migration_directory)
    run.verify_called()


@pytest.mark.unit
@tempdir()
@patch('subprocess.run')
def test_mongo_facade_capture(run: Mock, temp_directory: TempDirectory) -> None:
    migration_directory = make_directory(temp_directory, "migration")
    assert os.path.exists(migration_directory)
    mongo_configuration = FakeMongoConfiguration()
    mongo_configuration.custom_connection_string = connection_string
    mongo_facade = MongoFacade()

    mongo_facade.capture_database_to_directory(mongo_configuration, migration_directory, "testname.gz")

    assert os.path.exists(migration_directory)
    run.verify_called()


def make_directory(temp_directory: TempDirectory, name: str) -> str:
    path = os.path.join(temp_directory.path, name)
    os.mkdir(path)
    return path


class FakeMongoConfiguration(MongoConfiguration):
    def __init__(self):
        super().__init__({})
        self.custom_password = ""
        self.custom_user = ""
        self.custom_connection_string = ""
        self.custom_port = ""
        self.custom_collection_name = "test"
        self.custom_host_name = ""

    @property
    def password(self) -> str:
        return self.custom_password

    @property
    def user(self) -> str:
        return self.custom_user

    @property
    def connection_string(self) -> str:
        return self.custom_connection_string

    @property
    def port(self) -> str:
        return self.custom_port

    @property
    def collection_name(self) -> str:
        return self.custom_collection_name

    @property
    def host_name(self) -> str:
        return self.custom_host_name
