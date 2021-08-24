import pytest as pytest

from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade

connection_string = "mongodb://127.17.0.5:27017/?gssapiServiceName=mongodb"


@pytest.mark.unit
def test_mongo_facade_capture() -> None:
    mongo_facade = MongoFacade()
    mongo_configuration = FakeMongoConfiguration()
    mongo_configuration.custom_connection_string = connection_string
    mongo_configuration.custom_host_name = "127.0.0.1"
    mongo_configuration.custom_port = "27017"
    mongo_facade.capture_mongo_collection_to_directory(
        mongo_configuration,
        "C:\\Users\\cnunnall\\Documents\\migration",
        "testname.gz")


@pytest.mark.unit
def test_mongo_facade_restore() -> None:
    mongo_facade = MongoFacade()
    mongo_configuration = FakeMongoConfiguration()
    mongo_configuration.custom_connection_string = connection_string
    mongo_configuration.custom_host_name = "127.0.0.1"
    mongo_configuration.custom_port = "27017"
    mongo_facade.restore_mongo_collection_from_directory(
        mongo_configuration,
        "C:\\Users\\cnunnall\\Documents\\migration",
        "testname.gz")


class FakeMongoConfiguration(MongoConfiguration):
    def __init__(self):
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
