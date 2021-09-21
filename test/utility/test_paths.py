from nislmigrate.utility.paths import (
    get_ni_application_data_directory_path,
    get_ni_shared_directory_64_path
)
import os
import pytest as pytest
import sys
from unittest.mock import patch
try:
    import winreg
except ImportError:
    pass  # Ignore on non-Windows


if not sys.platform.startswith('win'):
    pytest.skip('skipping windows-only tests', allow_module_level=True)


@pytest.mark.unit
@patch('winreg.OpenKey')
@patch('winreg.QueryValueEx')
def test_get_ni_application_data_directory_path_returns_configured_path(query_value_ex, open_key):
    open_key.return_value = FakeRegKey()
    path = 'd:\\My Custom Path\\NI'
    query_value_ex.return_value = (path, winreg.REG_SZ)

    assert path == get_ni_application_data_directory_path()


@pytest.mark.unit
@patch('winreg.OpenKey')
def test_get_ni_application_data_directory_path_returns_default_if_not_configured(open_key):
    open_key.side_effect = RuntimeError

    expected_path = os.path.join(
        str(os.environ.get('ProgramData')),
        'National Instruments',
    )
    return expected_path == get_ni_application_data_directory_path()


@pytest.mark.unit
@patch('winreg.OpenKey')
@patch('winreg.QueryValueEx')
def test_get_ni_shared_directory_64_path_returns_configured_path(query_value_ex, open_key):
    open_key.return_value = FakeRegKey()
    path = 'q:\\Some Path\\NI\\Shared'
    query_value_ex.return_value = (path, winreg.REG_SZ)

    assert path == get_ni_shared_directory_64_path()


@pytest.mark.unit
@patch('winreg.OpenKey')
def test_get_ni_shared_directory_64_path_throws_runtime_error_if_not_configured(open_key):
    open_key.side_effect = RuntimeError

    expected_path = os.path.join(
        str(os.environ.get('ProgramW6432')),
        'National Instruments',
        'Shared'
    )
    return expected_path == get_ni_shared_directory_64_path()


class FakeRegKey(object):
    def __enter__(self):
        pass

    def __exit__(self, _type, _value, _traceback):
        pass
