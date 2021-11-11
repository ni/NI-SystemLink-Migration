import os

import pytest

from nislmigrate.argument_handler import ArgumentHandler, CAPTURE_ARGUMENT
from nislmigrate.argument_handler import RESTORE_ARGUMENT
from nislmigrate.argument_handler import MIGRATION_DIRECTORY_ARGUMENT
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.migration_facilitator import MigrationFacilitator, CAN_NOT_MIGRATE_AND_LIST_INSTALLED_SERVICES_ERROR
from test.test_utilities import FakeFacadeFactory

test_migration_directory = os.path.join(os.path.abspath(os.sep), 'migration_test')


@pytest.mark.unit
def test_missing_migration_directory() -> None:
    test_arguments = [
        RESTORE_ARGUMENT,
        '--tags',
        '--' + MIGRATION_DIRECTORY_ARGUMENT + '=' + test_migration_directory,
        '--force',
    ]
    facade_factory = FakeFacadeFactoryWithRealMongoFacade()
    argument_handler = ArgumentHandler(test_arguments, facade_factory=facade_factory)
    migrator = MigrationFacilitator(facade_factory, argument_handler)

    with pytest.raises(FileNotFoundError):
        migrator.migrate()


@pytest.mark.unit
def test_missing_service_migration_file() -> None:
    test_arguments = [
        RESTORE_ARGUMENT,
        '--tags',
        '--' + MIGRATION_DIRECTORY_ARGUMENT + '=' + test_migration_directory,
        '--force',
    ]
    facade_factory = FakeFacadeFactoryWithRealMongoFacade()
    argument_handler = ArgumentHandler(test_arguments, facade_factory=facade_factory)
    migrator = MigrationFacilitator(facade_factory, argument_handler)

    with pytest.raises(FileNotFoundError):
        migrator.migrate()


@pytest.mark.unit
def test_list_installed_services_while_capturing_raises_error() -> None:
    test_arguments = [
        CAPTURE_ARGUMENT,
        '--list-installed-services',
        '--tags',
        '--' + MIGRATION_DIRECTORY_ARGUMENT + '=' + test_migration_directory,
    ]
    facade_factory = FakeFacadeFactoryWithRealMongoFacade()
    argument_handler = ArgumentHandler(test_arguments, facade_factory=facade_factory)
    migrator = MigrationFacilitator(facade_factory, argument_handler)

    with pytest.raises(MigrationError) as e:
        migrator.migrate()
        assert e == CAN_NOT_MIGRATE_AND_LIST_INSTALLED_SERVICES_ERROR


@pytest.mark.unit
def test_list_installed_services_while_restoring_raises_error() -> None:
    test_arguments = [
        RESTORE_ARGUMENT,
        '--list-installed-services',
        '--tags',
        '--' + MIGRATION_DIRECTORY_ARGUMENT + '=' + test_migration_directory,
        '--force',
    ]
    facade_factory = FakeFacadeFactoryWithRealMongoFacade()
    argument_handler = ArgumentHandler(test_arguments, facade_factory=facade_factory)
    migrator = MigrationFacilitator(facade_factory, argument_handler)

    with pytest.raises(MigrationError) as e:
        migrator.migrate()
        assert e == CAN_NOT_MIGRATE_AND_LIST_INSTALLED_SERVICES_ERROR


class FakeFacadeFactoryWithRealMongoFacade(FakeFacadeFactory):
    def __init__(self):
        super().__init__()
        self.real_mongo_facade: MongoFacade = MongoFacade(self.process_facade)

    def get_mongo_facade(self) -> MongoFacade:
        return self.real_mongo_facade
