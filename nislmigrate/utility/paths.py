import os
try:
    import winreg
except ImportError:
    pass  # Ignore on non-Windows


def get_ni_application_data_directory_path() -> str:
    """
    Looks up the NI application data directory using the configuration in the Windows registry.

    :return: A path like c:\\ProgramData\\National Instruments
    """
    if os.name != 'nt':
        raise RuntimeError('Operation is not currently supported on non-Windows')

    try:
        return __get_ni_installer_path('NIPUBAPPDATADIR')
    except Exception:
        # If not found, we will probably fail, but go ahead and use the OS default.
        # This is mostly for convenience of the unit tests.
        return os.path.join(
            str(os.environ.get('ProgramData')),
            'National Instruments',
        )


def get_ni_shared_directory_64_path() -> str:
    """
    Looks up the NI shared directory for 64-bit applications using the configuration
    in the Windows registry.

    :return: A path like C:\\Program Files\\National Instruments\\Shared\
    """
    if os.name != 'nt':
        raise RuntimeError('Operation is not currently supported on non-Windows')

    try:
        return __get_ni_installer_path('NISHAREDDIR64')
    except Exception:
        # If not found, we will probably fail, but go ahead and use the OS default.
        # This is mostly for convenience of the unit tests.
        return os.path.join(
            str(os.environ.get('ProgramW6432')),
            'National Instruments',
            'Shared'
        )


def __get_ni_installer_path(value_name: str) -> str:
    with winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        'SOFTWARE\\National Instruments\\Common\\Installer',
        0,
        winreg.KEY_READ
    ) as key:
        (directory, _) = winreg.QueryValueEx(key, value_name)
        return directory
