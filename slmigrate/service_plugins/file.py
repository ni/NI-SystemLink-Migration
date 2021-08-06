from slmigrate.service import ServicePlugin


class FilePlugin(ServicePlugin):

    @property
    def names(self):
        return ["fis", "file", "files"]

    @property
    def help(self):
        return "Migrate ingested files"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
