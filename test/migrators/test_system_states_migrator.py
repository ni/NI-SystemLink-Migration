from nislmigrate.migrators.system_states_migrator import SystemStatesMigrator, GIT_REPO_CONFIG_CONFIGURATION_KEY
import os
from pathlib import Path
import pytest
from testfixtures import tempdir
from test.test_utilities import FakeFacadeFactory, FakeFileSystemFacade
from typing import Any, Dict, Tuple


@pytest.mark.unit
@tempdir()
def test_file_migrator_does_not_copy_nonexistant_git_repo(directory):
    git_path = os.path.join(directory.path, 'git')
    facade_factory, file_system_facade = configure_facade_factory(git_path)
    migrator = SystemStatesMigrator()

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory is None


@pytest.mark.unit
@tempdir()
def test_file_migrator_copies_existing_git_repo(directory):
    git_path = os.path.join(directory.path, 'git')
    make_directory_with_contents(git_path)
    facade_factory, file_system_facade = configure_facade_factory(git_path)
    migrator = SystemStatesMigrator()

    migrator.capture('data_dir', facade_factory, {})

    assert file_system_facade.last_from_directory == git_path


def configure_facade_factory(git_path: str) -> Tuple[FakeFacadeFactory, FakeFileSystemFacade]:
    facade_factory = FakeFacadeFactory()

    file_system_facade = facade_factory.file_system_facade
    properties: Dict[str, Any] = {
            'Mongo.CustomConnectionString': 'mongodb://localhost',
            'Mongo.Database': 'nisystemstate',
            GIT_REPO_CONFIG_CONFIGURATION_KEY: git_path
        }
    file_system_facade.config = {
            'SystemsState': properties
        }

    return (facade_factory, file_system_facade)


def make_directory_with_contents(path: str):
    os.mkdir(path)
    file_path = os.path.join(path, 'a_file')
    Path(file_path).touch()
