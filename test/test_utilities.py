from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade


class FakeServiceManager(SystemLinkServiceManagerFacade):
    are_services_running = True

    def stop_all_system_link_services(self) -> None:
        self.are_services_running = False

    def start_all_system_link_services(self) -> None:
        self.are_services_running = True
