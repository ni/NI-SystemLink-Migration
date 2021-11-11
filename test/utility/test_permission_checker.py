from unittest.mock import patch
import pytest as pytest
from nislmigrate.utility.permission_checker import PermissionChecker


@pytest.mark.unit
@patch('ctypes.windll.shell32.IsUserAnAdmin')
def test_is_running_with_elevated_permissions_on_windows_returns_true(is_user_admin):
    is_user_admin.return_value = True

    assert PermissionChecker.is_running_with_elevated_permissions()


@pytest.mark.unit
@patch('ctypes.windll.shell32.IsUserAnAdmin')
def test_is_running_with_non_elevated_permissions_on_windows_returns_false(is_user_admin):
    is_user_admin.return_value = False

    assert not PermissionChecker.is_running_with_elevated_permissions()


@pytest.mark.unit
@patch('ctypes.windll.shell32.IsUserAnAdmin')
def test_verify_elevated_permissions_does_not_raise_exception(is_user_admin):
    is_user_admin.return_value = True

    PermissionChecker.verify_elevated_permissions()


@pytest.mark.unit
@patch('ctypes.windll.shell32.IsUserAnAdmin')
def test_verify_elevated_permissions_raises_exception(is_user_admin):
    is_user_admin.return_value = False

    with pytest.raises(PermissionError):
        PermissionChecker.verify_elevated_permissions()
