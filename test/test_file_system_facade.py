import os
from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.utility import permission_checker
from testfixtures import tempdir

import pytest

@pytest.mark.unit
@tempdir()
# @patch('ctypes.windll.shell32.IsUserAnAdmin')
def test_copy_directory(directory):
    source_path = os.path.join(directory.path, "source")
    destination_path = os.path.join(directory.path, "destination")
    os.mkdir(source_path)
    os.mkdir(destination_path)
    file_path = os.path.join(source_path, "demofile3.txt")
    destination_file_path = os.path.join(destination_path, "demofile3.txt")
    file = open(file_path, "w")
    file.close()

    file_system_facade = FileSystemFacade()
    file_system_facade.copy_directory(source_path, destination_path)

    assert os.path.isfile(destination_file_path)