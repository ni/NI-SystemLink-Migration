from slmigrate.service import ServicePlugin


class FilePlugin(ServicePlugin):

    @property
    def names(self):
        return ["notification", "notifications", ]

    @property
    def help(self):
        return "Migrate notifications strategies, templates, and groups"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
