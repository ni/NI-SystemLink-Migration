from slmigrate.service import ServicePlugin


class UserDataPlugin(ServicePlugin):

    @property
    def names(self):
        return ["userdata", "ud", ]

    @property
    def help(self):
        return "Migrate user data"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
