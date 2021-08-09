from nislmigrate.service import ServicePlugin


class FilePlugin(ServicePlugin):

    @property
    def names(self):
        return ["states", "state", ]

    @property
    def help(self):
        return "Migrate system states"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
