from slmigrate.service import ServicePlugin


class OPCPlugin(ServicePlugin):

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
