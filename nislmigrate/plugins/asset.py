from nislmigrate.service import ServicePlugin


class AssetPlugin(ServicePlugin):

    @property
    def names(self):
        return ["asset", "assets"]

    @property
    def help(self):
        return "Migrate asset utilization and calibration data"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
