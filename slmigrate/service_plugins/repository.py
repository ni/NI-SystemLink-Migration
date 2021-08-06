from slmigrate.service import ServicePlugin


class RepositoryPlugin(ServicePlugin):

    @property
    def names(self):
        return ["repository", "repo"]

    @property
    def help(self):
        return "Migrate packages and feeds"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
