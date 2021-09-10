import pytest
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin
from nislmigrate.migration_action import MigrationAction
from nislmigrate.migration_facilitator import MigrationFacilitator
from test.test_utilities import FakeFacadeFactory, FakeArgumentHandler


@pytest.mark.unit
def test_migrate_pre_restore_error_check_called_on_migrator_with_same_migration_directory_as_restore():
    fake_migrator = FakeMigrator()
    facade_factory = FakeFacadeFactory()
    argument_handler = FakeArgumentHandler([fake_migrator], MigrationAction.RESTORE)
    facilitator = MigrationFacilitator(facade_factory, argument_handler)

    facilitator.migrate()

    assert fake_migrator.pre_restore_migration_directory == fake_migrator.restore_migration_directory
    assert fake_migrator.pre_restore_count == 1
    assert fake_migrator.restore_count == 1


class FakeMigrator(MigratorPlugin):
    def __init__(self):
        self.pre_restore_migration_directory: str = ''
        self.restore_migration_directory: str = ''
        self.restore_count = 0
        self.pre_restore_count = 0

    @property
    def argument(self) -> str:
        return self.name.lower()

    @property
    def name(self) -> str:
        return 'Fake'

    @property
    def help(self) -> str:
        return f'{self.name} help'

    def capture(self, migration_directory, facade_factory, arguments) -> None:
        pass

    def restore(self, migration_directory, facade_factory, arguments) -> None:
        self.restore_count += 1
        self.restore_migration_directory = migration_directory

    def pre_restore_check(self, migration_directory, facade_factory, arguments) -> None:
        self.pre_restore_count += 1
        self.pre_restore_migration_directory = migration_directory
