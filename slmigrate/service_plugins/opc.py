from slmigrate.service import ServicePlugin

class OPCPlugin(ServicePlugin):

    @property
    def names(self):
        return ["opc", "opcua", "opcuaclient"]

    @property
    def help(self):
        return "Migrate OPCUA sessions and certificates"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass