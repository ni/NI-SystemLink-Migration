"""
Utility function to read the README file which is used for the long_description of the python package.
"""

from pathlib import Path
from setuptools import setup
from slmigrate import __version__


def read_requirements(filename):
    """
    Reads the contents of a requirements file located next to this module.

    :param filename: The name of the python requirements file.
    :return: The list of requirements.
    """
    return read(filename).splitlines()


def read(file_name):
    """
    Reads the contents of a file located next to this module.

    :param file_name: The name of the file to read.
    :return: The entire contents of the file.
    """
    return open(Path(__file__).parent / file_name).read()


settings = dict(
    name="slmigrate",
    packages=["slmigrate"],
    version=__version__,
    author="prestwick",
    author_email="",
    description=("Migrate various SystemLink data and configuration between servers"),
    license="MIT",
    keywords="slmigrate",
    url="https://github.com/prestwick/systemlink-migration-sandbox",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    install_requires=read_requirements("requirements.txt"),
    tests_require=read_requirements("test-requirements.txt"),
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
)

if __name__ == "__main__":
    setup(**settings)
