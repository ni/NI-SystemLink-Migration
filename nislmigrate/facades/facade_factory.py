from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.mongo_facade import MongoFacade


class FacadeFactory:
    """
    Provides instances of objects capable of migrating databases or files.
    """
    def __init__(self):
        """
        Creates a new instance of MigratorFactory.
        """
        self.mongo_facade: MongoFacade = MongoFacade()
        self.file_system_facade: FileSystemFacade = FileSystemFacade()

    def get_mongo_facade(self) -> MongoFacade:
        """
        Gets a MongoMigrator instance.
        """
        return self.mongo_facade

    def get_file_system_facade(self) -> FileSystemFacade:
        """
        Gets a FileMigrator instance.
        """
        return self.file_system_facade
