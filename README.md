# systemlink-migration-sandbox
A place for example PowerShell scripts used to migrate data and setting between SystemLink servers. We encourage migration to servers with a fresh install of SystemLink that contains no production data. 

# Migrating with systemlinkmigrate.py

## Prerequisites 
### SystemLink
- These scripts assume migration from a SystemLink 2020R1 (20.0) to another SystemLink 2020R1 server 
- These scripts assume a single-box SystemLink installation. 
- These scripts are designed to un on the same machines as the SystemLink installation. They do not support remote migration.

### Python
- These scripts require >=Python3 to run. Installers can be found at [python.org](https://www.python.org/downloads/)
- The documentation in this repo assumes Python has been added to your **PATH**. 
- Depending on the setup of your environment you may invoke python with `python`, `python3`, or `py`. Documentation in this repo use `py`. 

## Running systemlinkmigrate.py
### Basic usage

```bash
py systemlinkmigrate.py --capture --tags
```
Running `systemlinkmigrate.py` with the above arguments will capture tag and tag history and store this data in `C:\migration`. 

```bash
py systemlinkmigrate.py --restore --tags
```

Running `systemlinkmigrate.py` with the above arguments will restore tag and tag history data from the directory `C:\migration`.

### Capture and Restore
The `--capture` and `--restore` arguments determine the directionality of the migration. The `--capture` argument is used when migrating data FROM an existing SystemLink server. The `--restore` argument is used when migrating data TO a new SystemLink server. At least one of these arguments must be specified and both arguments cannot be used simultaneously. 

### Specifying services to migrate
To migrate the data associated with a SystemLink service you must specify the service as an argument. Multiple services may be captured or restored by providing multiple arguments; e.g.

```bash
py systemlinkmigrate.py --capture --tags --opc
```

#### Supported Services
The following services can be migrated with this utility:

- Tag Ingestion and Tag History: `--tag`
- Tag Alarm Rules: `--alarm`
- OPCUA Client: `--opc`
- File Ingestion: `--file`
- Test Monitor: `--test`

## Specifying a Migration Directory
By default this tool will migrate data into the directory `C:\migrate`. During *capture* this directory is created. During *restore* this directory is expected to be present. The `--dir` argument allows for other directories and locations to be specified. For example:
```bash
py systemlinkmigrate.py --capture --tag --dir="C:\migrate_8-3-2020
````
These arguments will capture tag and tag history data and store them in the directory `C:\migrate_8-3-2020`


# Extending systemlinkmigrate.py
The `systemlinkmigrate.py` utility can be extended to migrate services whose data is within MongoDB, a single file, or directory. For data not covered by these additional changes may be needed that are not covered in this README. 

## Getting started for development
Like SystemLink this tool is designed to be developed, tested, and run on Windows. 
- Install Python3, pip, and Make
- Run `make install`
- Run `test/dlmongo.ps1`
- Run `make tests`

If these steps execute/pass you are ready for development

## Adding a new service dictionary constant
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

## Adding new arguments
A new service will require new arguments to be passed from the command line. This can all be done in `slmigrate/arghander.py/parse_arguments`. Be sure to use the value from the service dictionary for specifying the primary argument as this is used to look up the dictionary in `determiner_migrate_action`. Additional alias arguments may be specified. For example:

```python
parser.add_argument("--" + constants.opc.arg, "--opcua", "--opcuaclient", help="Migrate OPCUA sessions and certificates", action="store_true")
    
```

## Tests and CI
By and large tests should be agnostic to a particular service, and use the `test_service` in `slmigrate/test/test_constants.py` whenever possible. Please note that constants in `test_constants.py` are not used directly and instead overwrite analogous constants in `constants.py`. This allows functions to be tested more directly and not contain conditional logic for test case, which in turn allows test to be run on a CI without SystemLink installed. 

All tests must pass and all code pass `flake8` linting before new code to be checked into `master`. 
