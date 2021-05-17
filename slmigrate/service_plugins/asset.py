from slmigrate.service import ServicePlugin

class AssetPlugin(ServicePlugin):

    @property
    def names(self):
        return ["asset", "assets",]

    @property
    def help(self):
        return "Migrate asset utilization and calibration data"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass