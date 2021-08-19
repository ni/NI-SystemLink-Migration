# Contributing to NI-SystemLink-Migration

Contributions to **NI-SystemLink-Migration** are welcome from all!

**NI-SystemLink-Migration** is managed via [git](https://git-scm.com), with the canonical upstream
repository hosted on [GitHub](https://github.com/ni/NI-SystemLink-Migration).

**NI-SystemLink-Migration** follows a pull-request model for development.  If you wish to
contribute, you will need to create a GitHub account, fork this project, push a
branch with your changes to your project, and then submit a pull request.

See [GitHub's official documentation](https://help.github.com/articles/using-pull-requests/) for more details.

## Development
### Getting started
To get the source code for this tool, simply clone this repository:
```bash
git clone https://github.com/ni/NI-SystemLink-Migration.git
cd NI-SystemLink-Migration
```
This tool uses poetry to manage project dependencies, install poetry using:
```bash
pip install poetry
```
To install the dependencies for the migration tool project, run:
```bash
poetry install
```
Finally, to run the tool while developing, use the poetry `run` command:
```bash
poerty run nislmigrate
```
### Running tests
The unit tests in this repository can be executed using `pytest` or `tox`:
```bash
# Run all unit tests:
poerty run pytest
# Run all unit tests using all supported python versions:
poerty run tox
```
### Code style
The python code style in this repository adheres to the `flake8` linters default configuration. Linting can be run on the repository using:"
```bash
poerty run flake8
```

### Extensibility
Additional backup/restore strategies can be easily added using the `ServicePlugin` abstract base class:
1. Add a new python class to the `plugins` module that implements the `ServicePlugin` class:
```python
from nislmigrate.service import ServicePlugin
from nislmigrate.migrator_factory import MigratorFactory

class CustomMigration(ServicePlugin):

    @property
    def names(self):
        return ["custom-migration", "cm"]

    @property
    def help(self):
        return "Performs some custom migration action"

    def capture(self, migration_directory: str, migrator_factory: MigratorFactory):
        pass

    def restore(self, migration_directory: str, migrator_factory: MigratorFactory):
        pass
```
The migration tool will now run the `capture` or `restore` method of your custom migration strategy if run with the custom flag:
```bash
poetry run nislmigrate capture --custom-migration
poetry run nislmigrate restore --custom-migration
```

## Contributing

After you've verified that you can successfully run the unit tests and they all pass for
**NI-SystemLink-Migration**, you can begin contributing to to the project.

1. Write a failing test for the new feature / bugfix.
1. Make your change.
1. Verify all tests, including the new ones, pass.
1. On GitHub, send a new pull request to the main repository's master branch. GitHub
   pull requests are the expected method of code collaboration on this project.
1. Add at least one reviewer to the pull request and wait for thier approval.
1. Merge the pull request into master
   
## Releasing
A new version of this tool is released when the `version` property in `pyproject.toml` is changed.

## Developer Certificate of Origin (DCO)

   Developer's Certificate of Origin 1.1

   By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.

(taken from [developercertificate.org](https://developercertificate.org/))

See [LICENSE](https://github.com/ni/NI-SystemLink-Migration/blob/main/LICENSE)
for details about how **NI-SystemLink-Migration** is licensed.