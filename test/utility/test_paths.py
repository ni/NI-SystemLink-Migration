from nislmigrate.utility.paths import (
    get_ni_application_data_directory_path,
    get_ni_shared_directory_64_path
)
import os
import pytest as pytest
from unittest.mock import patch
import winreg


@pytest.mark.unit
@patch('winreg.QueryValueEx')
def test_get_ni_application_data_directory_path_returns_configured_path(query_value_ex):
    path = 'd:\\My Custom Path\\NI'
    query_value_ex.return_value = (path, winreg.REG_SZ)

    assert path == get_ni_application_data_directory_path()


@pytest.mark.unit
@patch('winreg.QueryValueEx')
def test_get_ni_application_data_directory_path_returns_default_if_not_configured(query_value_ex):
    query_value_ex.side_effect = RuntimeError

    expected_path = os.path.join(
        str(os.environ.get('ProgramData')),
        'National Instruments',
    )
    return expected_path == get_ni_application_data_directory_path()


@pytest.mark.unit
@patch('winreg.QueryValueEx')
def test_get_ni_shared_directory_64_path_returns_configured_path(query_value_ex):
    path = 'q:\\Some Path\\NI\\Shared'
    query_value_ex.return_value = (path, winreg.REG_SZ)

    assert path == get_ni_shared_directory_64_path()


@pytest.mark.unit
@patch('winreg.QueryValueEx')
def test_get_ni_shared_directory_64_path_throws_runtime_error_if_not_configured(query_value_ex):
    query_value_ex.side_effect = RuntimeError

    expected_path = os.path.join(
        str(os.environ.get('ProgramW6432')),
        'National Instruments',
        'Shared'
    )
    return expected_path == get_ni_shared_directory_64_path()
