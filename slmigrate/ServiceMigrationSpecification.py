from slmigrate.MigrationAction import MigrationAction

class ServiceMigrationSpecification:
    service_info = ""
    migration_action = MigrationAction.CAPTURE
    migration_directory = ""

    def __init__(self, service_info: str, migration_action: MigrationAction, migration_directory: str):
        self.service_info = service_info
        self.migration_action = migration_action
        self.migration_directory = migration_directory

    def __str__(self):
        if self.migration_action == MigrationAction.CAPTURE:
            return str(self.service_info.name) + " configured to be captured to " + str(self.migration_directory)
        elif self.migration_action == MigrationAction.RESTORE:
            return str(self.service_info.name) + " configured to be restored from " + str(self.migration_directory)