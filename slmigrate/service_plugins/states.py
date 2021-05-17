from slmigrate.service import ServicePlugin

class FilePlugin(ServicePlugin):

    @property
    def names(self):
        return ["states", "state", ]

    @property
    def help(self):
        return "Migrate system states"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass