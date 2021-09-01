import os
import pytest
from testfixtures import tempdir, TempDirectory
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.logs.migration_error import MigrationError


@pytest.mark.unit
@tempdir()
def test_copy_directory(directory):
    source_path = make_directory(directory, "source")
    destination_path = make_directory(directory, "destination")
    make_file(source_path, "demofile3.txt")
    destination_file_path = os.path.join(destination_path, "demofile3.txt")
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_directory(source_path, destination_path, False)

    assert os.path.isfile(destination_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_directory_destination_directory_not_empty_raises_error(directory):
    source_path = make_directory(directory, "source")
    destination_path = make_directory(directory, "destination")
    make_file(source_path, "demofile3.txt")
    make_file(destination_path, "demofile2.txt")
    file_system_facade = FileSystemFacade()

    with pytest.raises(MigrationError):
        file_system_facade.copy_directory(source_path, destination_path, False)


@pytest.mark.unit
@tempdir()
def test_force_copy_directory_destination_directory_contents_deleted(directory):
    source_path = make_directory(directory, "source")
    destination_path = make_directory(directory, "destination")
    deleted_file_path = make_file(destination_path, "demofile2.txt")
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_directory(source_path, destination_path, True)

    assert not os.path.exists(deleted_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_directory_source_directory_does_not_exist_raises_error(directory):
    source_path = os.path.join(directory.path, "source")
    destination_path = make_directory(directory, "destination")
    file_system_facade = FileSystemFacade()

    with pytest.raises(MigrationError):
        file_system_facade.copy_directory(source_path, destination_path, False)


@pytest.mark.unit
@tempdir()
def test_copy_file(directory):
    source_path = make_directory(directory, "source")
    destination_path = make_directory(directory, "destination")
    make_file(source_path, "demofile3.txt")
    destination_file_path = os.path.join(destination_path, "demofile3.txt")
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_file(source_path, destination_path, "demofile3.txt")

    assert os.path.exists(destination_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_file_does_not_copy_wrong_file(directory):
    source_path = make_directory(directory, "source")
    destination_path = make_directory(directory, "destination")
    make_file(source_path, "demofile3.txt")
    make_file(source_path, "demofile2.txt")
    unwanted_file_path = os.path.join(destination_path, "demofile2.txt")
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_file(source_path, destination_path, "demofile3.txt")

    assert not os.path.exists(unwanted_file_path)


def make_directory(temp_directory: TempDirectory, name: str) -> str:
    path = os.path.join(temp_directory.path, name)
    os.mkdir(path)
    return path


def make_file(path: str, name: str) -> str:
    file_path = os.path.join(path, name)
    file = open(file_path, "w")
    file.close()
    return file_path
