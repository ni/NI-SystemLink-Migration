from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migrator_plugin import MigratorPlugin


class OPCPlugin(MigratorPlugin):

    @property
    def names(self):
        return ["opc", "opcua", "opcuaclient"]

    @property
    def help(self):
        return "Migrate OPCUA sessions and certificates"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass
