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
    return __get_ni_installer_path('NIPUBAPPDATADIR')


def get_ni_shared_directory_64_path() -> str:
    """
    Looks up the NI shared directory for 64-bit applications using the configuration
    in the Windows registry.

    :return: A path like C:\\Program Files\\National Instruments\\Shared\
    """
    return __get_ni_installer_path('NISHAREDDIR64')


def __get_ni_installer_path(value_name: str) -> str:
    if os.name != 'nt':
        raise RuntimeError('Operation is not currently supported on non-Windows')

    try:
        with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\National Instruments\\Common\\Installer',
                0,
                winreg.KEY_READ) as key:
            (directory, _) = winreg.QueryValueEx(key, value_name)
            return directory
    except Exception:
        raise RuntimeError(f'{value_name} not configured. NI software may not be correctly installed.')
