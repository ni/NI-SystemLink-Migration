# NI-SystemLink-Migration tool `nislmigrate`
`nislmigrate` is a command line utility for migration, backup, and restore of supported SystemLink services.
# Installation
### Prerequisites
#### 1. SystemLink
- This tool currently supports migration from a SystemLink 2020R1 server, migration between other versions has not been tested.
- **We assume the server you are migrating to is clean with no data. Migrating to a server with existing data will result in data loss.**
- Not all services are supported yet, see **Supported Services** for details.
- This tool assumes a single-box SystemLink installation. 
- This tool must be run on the same machines as the SystemLink installations.
#### 2. Python
- This tool requires [Python 3.8](https://www.python.org/downloads/release/python-3811/) to run.
- The documentation in this repository assumes Python has been added to your [**PATH**](https://datatofish.com/add-python-to-windows-path/).
### Installation
The latest released version of the tool can be installed by running:
```bash
pip install nislmigrate
```
# Usage
### Backup
To backup the data for a service listed in the **Supported Services** section run the tool with elevated permissions and the `capture` option and the corresponding flag for each of the services you want to back up (e.g. `--tags`):
```bash
nislmigrate capture --tags
```
This will backup the data corresponding with each service into the default migration directory (`C:\Users\[user]\Documents\migration\`). You can specify a different migration directory using the `--dir [path]` option:
```bash
nislmigrate capture --tags --dir C:\custom-backup-location
```

### Restore

> :warning: Restore overwrites existing data on the server. Include the `--force` argument to allow the data to be overwritten.

To restore the data for a service listed in the **Supported Services** section run the tool with elevated permissions and the `restore` option and the corresponding flag for each of the services you want to restore (e.g. `--tags`):
```bash
nislmigrate restore --tags --force
```
This will restore the data corresponding with each service from the default migration directory (`C:\Users\[user]\Documents\migration\`). If your captured data is in a different directory that can be specified with the `--dir [path]` option:
```bash
nislmigrate restore --force --tags --dir C:\custom-backup-location
```

Include `--force` on with all restore commands to indicate that data on the server may be overwritten.

### Migration
To migrate from one SystemLink server instance (server A) to a different instance (server B):
1. Install the migration tool on server A and server B.
1. Follow the backup instructions to backup the data from server A.
1. Copy the data produced by the backup of server A on server B.
1. Ensure server B is a clean SystemLink install with no existing data.
1. Follow the restore instructions to restore the backed up data onto server B.

# Development
See `CONTRIBUTING.MD` for detailed instructions on developing, testing, and releasing the tool.

# Supported Services
The following services can be migrated with this utility:

- Tag Ingestion and Tag History: `--tags`
- File Ingestion: `--files` 
    - Must migrate file to the same storage location on the new System Link server.
- Notifications: `--notification`

There are plans to support the following services in the near future:
- Tag Alarm Rules: `--tagrule`
- Alarm Instances: `--alarms`
- OPC UA Client: `--opc`
- Test Monitor: `--tests`
- Asset Management: `--assets`
    - Cannot be migrated between 2020R1 and 2020R2 servers
- Repository: `--repo`
    - Feeds may require additional updates if servers used for migration have different domain names
- User Data: `--userdata`
- States: `--states`
    - Feeds may require additional updates if servers used for migration have different domain names
    - Cannot be migrated between 2020R1 and 2020R2 servers
- Security `--security`
  
The following list of services is explicitly not supported because of issues that arose when developing and testing migrating the service that will require changes to the service rather than the migration utility to enable support:
- Cloud Connector
