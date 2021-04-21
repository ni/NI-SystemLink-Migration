"""TODO: Complete documentation."""

from pathlib import Path

from setuptools import setup

from slmigrate import __version__


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(file_name):
    """TODO: Complete documentation.

    :param file_name:
    :return:
    """
    return open(Path(__file__).parent / file_name).read()


def read_requirements(filename):
    """TODO: Complete documentation.

    :param filename:
    :return:
    """
    with open(filename) as file:
        return file.read().splitlines()


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
