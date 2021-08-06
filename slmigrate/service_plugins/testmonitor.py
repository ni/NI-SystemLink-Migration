from slmigrate.service import ServicePlugin


class TestMonitorPlugin(ServicePlugin):

    @property
    def names(self):
        return ["testmonitor", "test", "tests"]

    @property
    def help(self):
        return "Migrate Test Monitor data"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
