from slmigrate.service import ServicePlugin

class FilePlugin(ServicePlugin):

    @property
    def names(self):
        return ["fis", "file", "files"]

    @property
    def help(self):
        return "Migrate ingested files"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass