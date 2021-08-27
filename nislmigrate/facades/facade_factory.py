from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.facades.system_link_service_manager_facade import SystemLinkServiceManagerFacade


class FacadeFactory:
    """
    Provides instances of objects that wrap other tools capable of
    more complex actions such as migrating databases, copying files,
    or interacting with other command line utilities.
    """
    def __init__(self):
        """
        Creates a new instance of MigratorFactory.
        """
        self.mongo_facade: MongoFacade = MongoFacade()
        self.file_system_facade: FileSystemFacade = FileSystemFacade()
        self.system_link_service_manager_facade: SystemLinkServiceManagerFacade = SystemLinkServiceManagerFacade()

    def get_mongo_facade(self) -> MongoFacade:
        """
        Gets a MongoFacade instance.
        """
        return self.mongo_facade

    def get_file_system_facade(self) -> FileSystemFacade:
        """
        Gets a FileSystemFacade instance.
        """
        return self.file_system_facade

    def get_system_link_service_manager_facade(self) -> SystemLinkServiceManagerFacade:
        """
        Gets a SystemLinkServiceManagerFacade instance.
        """
        return self.system_link_service_manager_facade
