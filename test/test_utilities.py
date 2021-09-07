from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.process_facade import ProcessFacade
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade


class FakeServiceManager(SystemLinkServiceManagerFacade):
    are_services_running = True

    def stop_all_system_link_services(self) -> None:
        self.are_services_running = False

    def start_all_system_link_services(self) -> None:
        self.are_services_running = True


class FakeMongoFacade(MongoFacade):
    is_mongo_running = True

    def __init__(self, process_facade: ProcessFacade):
        super().__init__(process_facade)

    def start_mongo(self):
        self.is_mongo_running = True

    def stop_mongo(self):
        self.is_mongo_running = False
