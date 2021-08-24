import os

from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin


class OPCMigrator(MigratorPlugin):

    @property
    def name(self):
        return "opcuaclient"

    @property
    def argument(self):
        return "opc"

    @property
    def help(self):
        return "Migrate OPCUA sessions and certificates"

    __ni_directory = os.path.join(os.environ.get("ProgramData"), "National Instruments")
    __data_directory = os.path.join(__ni_directory, "Skyline", "Data", "OpcClient")
    __singlefile = "dump.rdb"

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade = facade_factory.get_mongo_facade()
        file_facade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config)
        # TODO: Figure out if mongo migration is needed for OPC service.
        mongo_facade.capture_mongo_collection_to_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        # TODO: Capture the entire directory for opc service.
        file_facade.capture_singlefile(
            migration_directory,
            self.name,
            self.__data_directory,
            self.__singlefile)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        mongo_facade = facade_factory.get_mongo_facade()
        file_facade = facade_factory.get_file_system_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config)
        mongo_facade.restore_mongo_collection_from_directory(
            mongo_configuration,
            migration_directory,
            self.name)
        file_facade.restore_singlefile(
            migration_directory,
            self.name,
            self.__data_directory,
            self.__singlefile)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        mongo_facade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_mongo_collection_from_directory(migration_directory,
                                                                          self.name)


"""
opc_dict = {
    "arg": "opc",
    "name": "OpcClient",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "OpcClient",
    "source_dir": os.path.join(
        os.environ.get("ProgramData"), "National Instruments", "Skyline", "Data", "OpcClient"
    ),
}
"""
