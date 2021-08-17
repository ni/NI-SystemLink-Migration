"""Defines this directory as a regular python package."""

import toml
from pathlib import Path


def get_version():
    path = Path(__file__).resolve().parents[1] / 'pyproject.toml'
    project_configuration = toml.loads(open(str(path)).read())
    return project_configuration['tool']['poetry']['version']


__version__ = get_version()
