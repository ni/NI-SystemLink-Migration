from slmigrate.service import ServicePlugin

class AlarmRulePlugin(ServicePlugin):

    @property
    def names(self):
        return ["alarmrule", "alarms", "alarm",]

    @property
    def help(self):
        return "Migrate Tag alarm rules"

    def capture(self, args, mongohandler=None, filehandler=None):
        pass

    def restore(self, args, mongohandler=None, filehandler=None):
        pass