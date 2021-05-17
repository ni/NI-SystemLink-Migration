from slmigrate.service import ServicePlugin

class FilePlugin(ServicePlugin):

    @property
    def names(self):
        return ["notification", "notifications", ]

    @property
    def help(self):
        return "Migrate notifications strategies, templates, and groups"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass