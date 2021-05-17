from slmigrate.service import ServicePlugin

class RepositoryPlugin(ServicePlugin):

    @property
    def names(self):
        return ["repository", "repo",]

    @property
    def help(self):
        return "Migrate packages and feeds"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass