from nislmigrate.migrators.file_migrator import FileMigrator
from nislmigrate.migrators.mongo_migrator import MongoMigrator


class MigratorFactory:
    """
    Provides instances of objects capable of migrating databases or files.
    """
    def __init__(self):
        """
        Creates a new instance of MigratorFactory.
        """
        self.mongo_migrator = MongoMigrator()
        self.file_migrator = FileMigrator()

    def get_mongo_migrator(self) -> MongoMigrator:
        """
        Gets a MongoMigrator instance.
        """
        return self.mongo_migrator

    def get_file_migrator(self) -> FileMigrator:
        """
        Gets a FileMigrator instance.
        """
        return self.file_migrator
