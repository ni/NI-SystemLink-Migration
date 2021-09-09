from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.extensibility.migrator_plugin_loader import MigratorPluginLoader
from nislmigrate.facades.facade_factory import FacadeFactory
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

    @staticmethod
    def validate_can_restore_database_from_directory(
            directory: str,
            dump_name: str,
    ) -> None:
        pass


class FakeFacadeFactory(FacadeFactory):
    def __init__(self):
        super().__init__()
        self.process_facade = FakeProcessFacade()
        self.mongo_facade = FakeMongoFacade(self.process_facade)
        self.system_link_service_manager_facade = FakeServiceManager()


class FakeMigratorPluginLoader(MigratorPluginLoader):
    def __init__(self, migrators: List[MigratorPlugin]):
        self.__migrators = migrators

    def get_plugins(self) -> List[MigratorPlugin]:
        return self.__migrators
