# Migrating with systemlinkmigrate.py

## Prerequisites 
### SystemLink
- These scripts assume migration from a SystemLink 2020R1 (20.0) to another SystemLink 2020R1 or 2020R2 server 
    - **We assume the server you are migrating to is clean with no data. Migrating to a server with existing data will result in data loss.**
    - Not all services can be migrated from a 2020R1 server to a 2020R2 server. Please review **Supported Services** for details
- These scripts assume a single-box SystemLink installation. 
- These scripts are designed to run on the same machines as the SystemLink installation. They do not support remote migration.

### Python
- These scripts require >=Python3 to run. Installers can be found at [python.org](https://www.python.org/downloads/).
- The documentation in this repository assumes Python has been added to your **PATH**. 
- Depending on your environment you may invoke python with `python`, `python3`, or `py`. Documentation in this repository use `py`. 

## Running systemlinkmigrate.py
### Basic usage

```bash
py slmigrate.py capture --tags
```
Running `systemlinkmigrate.py` with the above arguments will capture tag and tag history and store this data in `C:\migration`. 

```bash
py slmigrate.py restore --tags
```

Running `systemlinkmigrate.py` with the above arguments will restore tag and tag history data from the directory `C:\migration`.

### Capture and Restore
The `capture` and `restore` actions determine the directionality of the migration. The `capture` action is used when migrating data FROM an existing SystemLink server. The `restore` action is used when migrating data TO a new SystemLink server. Both actions cannot be used simultaneously. 

### Specifying services to migrate
To migrate the data associated with a SystemLink service you must specify the service as an argument. Multiple services may be captured or restored by providing multiple arguments; e.g:

```bash
py slmigrate.py capture --tags --opc
```

#### Supported Services
The following services can be migrated with this utility:

- Tag Ingestion and Tag History: `--tag`
- Tag Alarm Rules: `--alarm`
- OPCUA Client: `--opc`
- File Ingestion: `--file`
- Test Monitor: `--test`
- Asset Management: `--asset`
    - Cannot be migrated between 2020R1 and 2020R2 servers
- Repository: `--repo`
    - Feeds may require additional updates if servers used for migration have different domain names
- User Data: `--userdata`
- Notifications: `--notification`
- States: `--states`
    - Feeds may require additional updates if servers used for migration have different domain names
    - Cannot be migrated between 2020R1 and 2020R2 servers

...with more on the way.

#### Service Not Supported
The following list of services is explicitly not supported because of issues that arose when developing and testing migrating the service that will require changes to the service rather than the migration utility to enable support. 
- Cloud Connector

## Specifying a Migration Directory
By default this tool will migrate data into the directory `C:\migrate`. During *capture* this directory is created. During *restore* this directory is expected to be present. The `--dir` argument allows for other directories and locations to be specified. For example:
```bash
py slmigrate.py --capture --tag --dir="C:\migrate_8-3-2020
````
These arguments will capture tag and tag history data and store them in the directory `C:\migrate_8-3-2020`

## Migrating tag history to nitaghistorian database
Due to a bug introduced in SystemLink 2020R2 it is possible for tag history data to be stored in the incorrect database within the MongoDB instance. **This bug only affects environments where a remote MongoDB server is used.** To determine if you are in this state connect a MongoShell or visual database tool such as [Mongo Compass](https://www.mongodb.com/products/compass) to your Mongo instance and check if the collections `metadata` and `values` are in the default authentication database (typically the `admin` database).
- Use the `thdbbug` action to correct this. Cannot be used simultaneously with other actions. 
- If you are using a database other than `admin` you can specify this with the `--sourcedb` argument For example
```bash
py systmelinkmigrate.py thdbbug --sourcedb myadmindb
```

# Extending systemlinkmigrate.py
The `systemlinkmigrate.py` utility can be extended to migrate services whose data is within MongoDB, a single file, or directory. For data not covered by these additional changes may be needed that are not covered in this README. 

See `CONTRIBUTING.md` for getting started with developing or extending this tool.
