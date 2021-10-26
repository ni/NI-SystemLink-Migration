import os
import pytest
from testfixtures import tempdir, TempDirectory
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.logs.migration_error import MigrationError


@pytest.mark.unit
@tempdir()
def test_copy_directory(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    destination_file_path = os.path.join(destination_path, 'demofile3.txt')
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_directory(source_path, destination_path, False)

    assert os.path.isfile(destination_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_directory_destination_directory_not_empty_raises_error(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    make_file(destination_path, 'demofile2.txt')
    file_system_facade = FileSystemFacade()

    with pytest.raises(MigrationError):
        file_system_facade.copy_directory(source_path, destination_path, False)


@pytest.mark.unit
@tempdir()
def test_force_copy_directory_destination_directory_contents_deleted(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    deleted_file_path = make_file(destination_path, 'demofile2.txt')
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_directory(source_path, destination_path, True)

    assert not os.path.exists(deleted_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_directory_source_directory_does_not_exist_raises_error(directory):
    source_path = os.path.join(directory.path, 'source')
    destination_path = make_directory(directory, 'destination')
    file_system_facade = FileSystemFacade()

    with pytest.raises(MigrationError):
        file_system_facade.copy_directory(source_path, destination_path, False)


@pytest.mark.unit
@tempdir()
def test_copy_directory_if_exists_source_directory_does_not_exist_returns_false(directory):
    source_path = os.path.join(directory.path, 'source')
    destination_path = make_directory(directory, 'destination')
    file_system_facade = FileSystemFacade()

    result = file_system_facade.copy_directory_if_exists(source_path, destination_path, False)
    assert not result


@pytest.mark.unit
@tempdir()
def test_copy_directory_if_exists_source_directory_exists_copies_data(directory):
    source_path = make_directory(directory, 'source')
    make_file(source_path, 'demofile.txt')
    destination_path = make_directory(directory, 'destination')
    file_system_facade = FileSystemFacade()

    result = file_system_facade.copy_directory_if_exists(source_path, destination_path, False)
    assert result
    destination_file_path = os.path.join(destination_path, 'demofile.txt')
    assert os.path.isfile(destination_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_file(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    destination_file_path = os.path.join(destination_path, 'demofile3.txt')
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_file(source_path, destination_path, 'demofile3.txt')

    assert os.path.exists(destination_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_file_does_not_copy_wrong_file(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    make_file(source_path, 'demofile2.txt')
    unwanted_file_path = os.path.join(destination_path, 'demofile2.txt')
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_file(source_path, destination_path, 'demofile3.txt')

    assert not os.path.exists(unwanted_file_path)


@pytest.mark.unit
@tempdir()
def test_remove_directory_removes_readonly_directory(directory):
    to_remove = make_directory(directory, 'to_remove')
    make_file(to_remove, 'some_file.txt')
    file_system_facade = FileSystemFacade()

    file_system_facade.remove_directory(to_remove)

    assert not os.path.exists(to_remove)


@pytest.mark.unit
@tempdir()
@pytest.mark.parametrize('should_exist', [(False), (True)])
def test_does_directory_exist_returns_directory_status(directory, should_exist: bool):
    to_check = conditionally_make_directory(directory, 'to_check', should_exist)
    file_system_facade = FileSystemFacade()

    assert should_exist == file_system_facade.does_directory_exist(to_check)


@pytest.mark.unit
@tempdir()
@pytest.mark.parametrize('should_exist', [(False), (True)])
def test_does_file_exist_returns_file_status(directory, should_exist: bool):
    sub_directory = make_directory(directory, 'sub')
    to_check = conditionally_make_file(sub_directory, 'to_check', should_exist)
    file_system_facade = FileSystemFacade()

    assert should_exist == file_system_facade.does_file_exist(to_check)


@pytest.mark.unit
@tempdir()
@pytest.mark.parametrize('should_exist', [(False), (True)])
def test_does_file_exist_in_directory_returns_file_status(directory, should_exist: bool):
    sub_directory = make_directory(directory, 'sub')
    conditionally_make_file(sub_directory, 'to_check', should_exist)
    file_system_facade = FileSystemFacade()

    exists = file_system_facade.does_file_exist_in_directory(sub_directory, 'to_check')
    assert should_exist == exists


@pytest.mark.unit
@tempdir()
def test_copy_directory_to_encrypted_file_creates_file_at_destination(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    encrypted_file_path = os.path.join(destination_path, 'encrypted_file')
    file_system_facade = FileSystemFacade()

    file_system_facade.copy_directory_to_encrypted_file(source_path, encrypted_file_path, 'password')

    assert os.path.exists(encrypted_file_path)


@pytest.mark.unit
@tempdir()
def test_copy_directory_to_encrypted_file_creates_when_file_already_exists_raises_error(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    encrypted_file_path = make_file(destination_path, 'encrypted_file')
    file_system_facade = FileSystemFacade()

    with pytest.raises(FileExistsError):
        file_system_facade.copy_directory_to_encrypted_file(source_path, encrypted_file_path, 'password')


@pytest.mark.unit
@tempdir()
def test_copy_directory_to_encrypted_file_creates_when_tar_file_already_exists_raises_error(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    make_file(directory.path, 'source.tar')
    encrypted_file_path = os.path.join(destination_path, 'encrypted_file')
    file_system_facade = FileSystemFacade()

    with pytest.raises(FileExistsError):
        file_system_facade.copy_directory_to_encrypted_file(source_path, encrypted_file_path, 'password')


@pytest.mark.unit
@tempdir()
def test_copy_directory_from_encrypted_file_decrypts_file(directory):
    source_path = make_directory(directory, 'source')
    destination_path = make_directory(directory, 'destination')
    make_file(source_path, 'demofile3.txt')
    encrypted_file_path = os.path.join(destination_path, 'encrypted_file')
    file_system_facade = FileSystemFacade()
    file_system_facade.copy_directory_to_encrypted_file(source_path, encrypted_file_path, 'password')

    file_system_facade.copy_directory_from_encrypted_file(encrypted_file_path, destination_path, 'password')

    assert os.path.isfile(os.path.join(destination_path, 'demofile3.txt'))


def make_directory(temp_directory: TempDirectory, name: str) -> str:
    path = os.path.join(temp_directory.path, name)
    os.mkdir(path)
    return path


def conditionally_make_directory(temp_directory: TempDirectory, name: str, should_exist: bool) -> str:
    if should_exist:
        return make_directory(temp_directory, name)
    else:
        return os.path.join(temp_directory.path, name)


def make_file(path: str, name: str) -> str:
    file_path = os.path.join(path, name)
    file = open(file_path, 'w')
    file.close()
    return file_path


def conditionally_make_file(parent: str, name: str, should_exist: bool) -> str:
    if should_exist:
        return make_file(parent, name)
    else:
        return os.path.join(parent, name)
