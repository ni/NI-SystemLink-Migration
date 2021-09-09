import pytest

from nislmigrate.argument_handler import ArgumentHandler
from nislmigrate.argument_handler import RESTORE_ARGUMENT
from nislmigrate.argument_handler import MIGRATION_DIRECTORY_ARGUMENT
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.migration_facilitator import MigrationFacilitator
from test import test_constants


@pytest.mark.unit
def test_missing_migration_directory() -> None:
    test_arguments = [
        RESTORE_ARGUMENT,
        '--tags',
        '--' + MIGRATION_DIRECTORY_ARGUMENT + '=' + test_constants.migration_dir,
    ]

    argument_handler = ArgumentHandler(test_arguments)

    migrator_factory = FacadeFactory()
    migrator = MigrationFacilitator(migrator_factory, argument_handler)

    with pytest.raises(FileNotFoundError):
        migrator.migrate()


@pytest.mark.unit
def test_missing_service_migration_file() -> None:
    test_arguments = [
        RESTORE_ARGUMENT,
        '--tags',
        '--' + MIGRATION_DIRECTORY_ARGUMENT + '=' + test_constants.migration_dir,
    ]

    argument_handler = ArgumentHandler(test_arguments)

    migrator_factory = FacadeFactory()
    migrator = MigrationFacilitator(migrator_factory, argument_handler)

    with pytest.raises(FileNotFoundError):
        migrator.migrate()
