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
        with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                'SOFTWARE\\National Instruments\\Common\\Installer',
                0,
                winreg.KEY_READ) as key:
            (directory, _) = winreg.QueryValueEx(key, 'NIPUBAPPDATADIR')
            return directory
    except Exception:
        raise RuntimeError('NIPUBAPPDATADIR not configured. NI software may not be correctly installed.')
