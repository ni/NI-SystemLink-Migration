from typing import Dict, Optional

MONGO_HOST_NAME_CONFIGURATION_KEY = 'Mongo.Host'
MONGO_DATABASE_NAME_CONFIGURATION_KEY = 'Mongo.Database'
MONGO_PORT_NAME_CONFIGURATION_KEY = 'Mongo.Port'
MONGO_USER_CONFIGURATION_KEY = 'Mongo.User'
MONGO_PASSWORD_CONFIGURATION_KEY = 'Mongo.Password'
MONGO_CUSTOM_CONNECTION_STRING_CONFIGURATION_KEY = 'Mongo.CustomConnectionString'


class MongoConfiguration:
    def __init__(self, service_config: Dict):
        self.service_config = service_config

    @property
    def password(self) -> Optional[str]:
        return self.service_config.get(MONGO_PASSWORD_CONFIGURATION_KEY)

    @property
    def user(self) -> Optional[str]:
        return self.service_config.get(MONGO_USER_CONFIGURATION_KEY)

    @property
    def connection_string(self) -> Optional[str]:
        return self.service_config.get(MONGO_CUSTOM_CONNECTION_STRING_CONFIGURATION_KEY)

    @property
    def port(self) -> Optional[str]:
        return self.service_config.get(MONGO_PORT_NAME_CONFIGURATION_KEY)

    @property
    def database_name(self) -> Optional[str]:
        return self.service_config.get(MONGO_DATABASE_NAME_CONFIGURATION_KEY)

    @property
    def host_name(self) -> Optional[str]:
        return self.service_config.get(MONGO_HOST_NAME_CONFIGURATION_KEY)
