# Contributing to NI-SystemLink-Migration

Contributions to **NI-SystemLink-Migration** are welcome from all!

**NI-SystemLink-Migration** is managed via [git](https://git-scm.com), with the canonical upstream
repository hosted on [GitHub](https://github.com/ni/NI-SystemLink-Migration).

**NI-SystemLink-Migration** follows a pull-request model for development.  If you wish to
contribute, you will need to create a GitHub account, fork this project, push a
branch with your changes to your project, and then submit a pull request.

See [GitHub's official documentation](https://help.github.com/articles/using-pull-requests/) for more details.

# Getting Started

Like SystemLink this tool is designed to be developed, tested, and run on Windows. 

1. Clone this repository `git clone https://github.com/ni/NI-SystemLink-Migration.git`.
2. Install Python3.6, pip, and tox.
3. Run the tool with `python systemlinkmigrage.py`.

# Testing

1. Install Python3, pip, and tox.
2. Run `test/dlmongo.ps1`.
3. Start at the repository root and run `tox` to run all of the unit tests.
4. If these steps execute/pass you are ready for development.

# Releasing
1. On the GitHub project's main page, click Releases (on the right-hand side), and create a new release.
2. Use a tag and release name based on the migration tool's current version, e.g. "v0.1.0" and "0.1.0", respectively.
3. Update the version number in the `VERSION` file in the root of this repository and post a PR.
4. After a sufficient amount of time (minutes), verify that the release shows up on PyPI.

# Contributing

After you've verified that you can successfully run the unit tests and they all pass for
**NI-SystemLink-Migration**, you can begin contributing to to the project.

1. Write a failing test for the new feature / bugfix.
2. Make your change.
3. Verify all tests, including the new ones, pass.
4. Update CHANGELOG.md if applicable.
5. On GitHub, send a new pull request to the main repository's master branch. GitHub
   pull requests are the expected method of code collaboration on this project.

## How to: Add a new service dictionary constant
Add a new dictionary describing the service in `slmigrate/constants.py`. Existing dictionaries in source can be used as models for new ones. It is assumed all services have data in MongoDB to be migrated. Take note if your service contains one or more files on disk that must be migrated, and include the appropriate key/values in the dictionary as needed. Be sure to use `SimpleNamespace` to enable calling dictionary items in a `dot.deliminted.fashion`. 
**Example**
```python
opc_dict = {
    'arg': 'opc', # Primary argument. Recommened this to match the variable named assigned with SimpleNamespace
    'name': "OpcClient", # This is the exact service name as found in JSOJ files in C:\ProgramData\National Instruments\Skyline\Config
    'directory_migration': True, # True because these service contains data within a directory
    'singlefile_migration': False, # False because these services does not migrate single files
    'migration_dir': os.path.join(migration_dir, "OpcClient"), # Name of migration directory for this service
    'source_dir': os.path.join(program_data_dir, "National Instruments", "Skyline", "Data", "OpcClient") # Directory containing service data to be migrated. 
}
opc = SimpleNamespace(**opc_dict) # call dictionary items in a dot.deliminted.fashion rather than access the dictionary directly
```

## How to: Add new arguments
A new service will require new arguments to be passed from the command line. This can all be done in `slmigrate/arghander.py/parse_arguments`. Be sure to use the value from the service dictionary for specifying the primary argument as this is used to look up the dictionary in `determiner_migrate_action`. Additional alias arguments may be specified. For example:

```python
parser.add_argument("--" + constants.opc.arg, "--opcua", "--opcuaclient", help="Migrate OPCUA sessions and certificates", action="store_true")
    
```

## How to: Add tests and follow CI guidelines
By and large tests should be agnostic to a particular service, and use the `test_service` in `slmigrate/test/test_constants.py` whenever possible. 

All tests must pass and all code pass `flake8` linting before new code to be checked into `master`, this is run automatically on each pull request targeted on main. 

# Developer Certificate of Origin (DCO)

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