from slmigrate.service import ServicePlugin

class UserDataPlugin(ServicePlugin):

    @property
    def names(self):
        return ["userdata", "ud", ]

    @property
    def help(self):
        return "Migrate user data"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass