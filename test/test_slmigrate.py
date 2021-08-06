"""Migration tests."""

import pytest

import slmigrate.constants as constants
from slmigrate.argument_handler import ArgumentHandler, RESTORE_ARGUMENT, MIGRATION_DIRECTORY_ARGUMENT
from slmigrate.file_handler import FileHandler
from slmigrate.mongo_handler import MongoHandler
from slmigrate.service_migrator import ServiceMigrator
from slmigrate.systemlink_service_manager import SystemLinkServiceManager
from test import test_constants


@pytest.mark.unit
def test_missing_migration_directory():
    """TODO: Complete documentation.

    :return:
    """
    test_arguments = [
        RESTORE_ARGUMENT,
        "--" + constants.tag.arg,
        "--" + MIGRATION_DIRECTORY_ARGUMENT + "=" + test_constants.migration_dir,
    ]

    argument_handler = ArgumentHandler(test_arguments)

    migrator = ServiceMigrator()
    migrator.mongo_handler = MongoHandler()
    migrator.file_handler = FileHandler()
    migrator.service_manager = SystemLinkServiceManager()

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
    migration_action = argument_handler.determine_migration_action()
    migration_directory = argument_handler.get_migration_directory()

    with pytest.raises(FileNotFoundError):
        migrator.migrate_services(services_to_migrate, migration_action, migration_directory)


@pytest.mark.unit
def test_missing_service_migration_file():
    """TODO: Complete documentation.

    :return:
    """
    test_arguments = [
        RESTORE_ARGUMENT,
        "--" + constants.tag.arg,
        "--" + MIGRATION_DIRECTORY_ARGUMENT + "=" + test_constants.migration_dir,
    ]

    argument_handler = ArgumentHandler(test_arguments)

    migrator = ServiceMigrator()
    migrator.mongo_handler = MongoHandler()
    migrator.file_handler = FileHandler()
    migrator.service_manager = SystemLinkServiceManager()

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
    migration_action = argument_handler.determine_migration_action()
    migration_directory = argument_handler.get_migration_directory()

    with pytest.raises(FileNotFoundError):
        migrator.migrate_services(services_to_migrate, migration_action, migration_directory)


@pytest.mark.unit
def test_missing_service_migration_dir():
    """TODO: Complete documentation.

    :return:
    """
    test_arguments = [
        RESTORE_ARGUMENT,
        "--" + constants.fis.arg,
        "--" + MIGRATION_DIRECTORY_ARGUMENT + "=" + test_constants.migration_dir,
    ]
    argument_handler = ArgumentHandler(test_arguments)

    migrator = ServiceMigrator()
    migrator.mongo_handler = MongoHandler()
    migrator.file_handler = FileHandler()
    migrator.service_manager = SystemLinkServiceManager()

    services_to_migrate = argument_handler.get_list_of_services_to_capture_or_restore()
    migration_action = argument_handler.determine_migration_action()
    migration_directory = argument_handler.get_migration_directory()

    with pytest.raises(FileNotFoundError):
        migrator.migrate_services(services_to_migrate, migration_action, migration_directory)
