from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.process_facade import ProcessFacade, BackgroundProcess
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade
from typing import List, Optional


class FakeServiceManager(SystemLinkServiceManagerFacade):
    are_services_running = True

    def stop_all_system_link_services(self) -> None:
        self.are_services_running = False

    def start_all_system_link_services(self) -> None:
        self.are_services_running = True


class NoopBackgroundProcess(BackgroundProcess):
    def __init__(self, arguments: List[str]):
        pass

    def stop(self):
        pass


class FakeProcessFacade(ProcessFacade):
    def run_process(self, args: List[str]):
        pass

    def run_background_process(self, args: List[str]) -> BackgroundProcess:
        return NoopBackgroundProcess(args)


class FakeMongoFacade(MongoFacade):
    is_mongo_running = True

    def __init__(self, process_facade: Optional[ProcessFacade] = None):
        super().__init__(process_facade or FakeProcessFacade())

    def start_mongo(self):
        self.is_mongo_running = True

    def stop_mongo(self):
        self.is_mongo_running = False
