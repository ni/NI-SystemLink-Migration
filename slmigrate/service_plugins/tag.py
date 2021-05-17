from slmigrate.service import ServicePlugin

class TagPlugin(ServicePlugin):

    @property
    def names(self):
        return ["tag", "tags", "tagingestion", "taghistory"]

    @property
    def help(self):
        return "Migrate tags and tag histories"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass