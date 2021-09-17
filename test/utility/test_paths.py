from nislmigrate.utility.paths import get_ni_application_data_directory_path
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
def test_get_ni_application_data_directory_path_throws_runtime_error_if_not_configured(query_value_ex):
    query_value_ex.side_effect = RuntimeError

    with pytest.raises(RuntimeError):
        get_ni_application_data_directory_path()
