from typing import Dict

MONGO_HOST_NAME_CONFIGURATION_KEY = "Mongo.Host"
MONGO_DATABASE_NAME_CONFIGURATION_KEY = "Mongo.Database"
MONGO_PORT_NAME_CONFIGURATION_KEY = "Mongo.Port"
MONGO_USER_CONFIGURATION_KEY = "Mongo.User"
MONGO_PASSWORD_CONFIGURATION_KEY = "Mongo.Password"
MONGO_CUSTOM_CONNECTION_STRING_CONFIGURATION_KEY = "Mongo.CustomConnectionString"


class MongoConfiguration:
    def __init__(self, service_config: Dict):
        self.service_config = service_config

    @property
    def password(self) -> str:
        return self.service_config[MONGO_PASSWORD_CONFIGURATION_KEY]

    @property
    def user(self) -> str:
        return self.service_config[MONGO_USER_CONFIGURATION_KEY]

    @property
    def connection_string(self) -> str:
        return self.service_config[MONGO_CUSTOM_CONNECTION_STRING_CONFIGURATION_KEY]

    @property
    def port(self) -> str:
        return self.service_config[MONGO_PORT_NAME_CONFIGURATION_KEY]

    @property
    def database_name(self) -> str:
        return self.service_config[MONGO_DATABASE_NAME_CONFIGURATION_KEY]

    @property
    def host_name(self) -> str:
        return self.service_config[MONGO_HOST_NAME_CONFIGURATION_KEY]
