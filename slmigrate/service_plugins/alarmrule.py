from slmigrate.service import ServicePlugin


class AlarmRulePlugin(ServicePlugin):

    @property
    def names(self):
        return ["alarmrule", "alarms", "alarm"]

    @property
    def help(self):
        return "Migrate Tag alarm rules"

    def capture(self, args, mongo_handler=None, file_handler=None):
        pass

    def restore(self, args, mongo_handler=None, file_handler=None):
        pass
