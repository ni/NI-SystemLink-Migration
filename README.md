# NI-SystemLink-Migration tool `nislmigrate`
`nislmigrate` is a command line utility for migration, backup, and restore of supported SystemLink services.

### Prerequisites
#### 1. SystemLink
- This tool offically supports migration between SystemLink versions 21.0, 21.1, 21.3, & 21.5. Other versions have not been tested.
- **We assume the server you are migrating to is clean with no data. Migrating to a server with existing data will result in data loss.**
- Services that are supported with any caveats and exceptions are detailed in the **Supported Services** section below.
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

To backup the data for a service listed in the **Supported Services** section run the tool with elevated permissions and use the `capture` option with the corresponding flag for each of the services you want to back up (e.g. `--security`):
```bash
nislmigrate capture --security
```
This will backup the data corresponding with each service into the default migration directory (`C:\Users\[user]\Documents\migration\`). You can specify a different migration directory using the `--dir [path]` option:
```bash
nislmigrate capture --security --dir C:\custom-backup-location
```
To backup the data for all supported services at once, the `--all` flag can be used instead of listing out each individual service. Using `--all` will require that you include the `--secret` flag for services that require encrypting backed up data for security:
```bash
nislmigrate capture --all --secret <password>
```

### Restore

> :warning: Restoring requires the `--force` flag to explicitly allow overwriting the existing data on the server. Without it, the command will fail.

To restore the data for a service listed in the **Supported Services** section run the tool with elevated permissions and  use the `restore` option with the corresponding flag for each of the services you want to restore (e.g. `--security`):
```bash
nislmigrate restore --security
```
This will restore the data corresponding with each service from the default migration directory (`C:\Users\[user]\Documents\migration\`). If your captured data is in a different directory that can be specified with the `--dir [path]` option:
```bash
nislmigrate restore --security --dir C:\custom-backup-location
```
To restore the data for all supported services at once, the `--all` flag can be used instead of listing out each individual service. Using `--all` will require that you include the `--secret` flag for services that require encrypting backed up data for security:
```bash
nislmigrate restore --all --secret <password>
```

### Migration
>:warning: Server A must be a clean SystemLink installation, any existing data will be deleted.

To migrate from one SystemLink server instance (`server A`) to a different instance (`server B`):
1. Install the migration tool on `server A` and `server B`.
1. Follow the backup instructions to backup the data from `server A`.
1. Copy the data produced by the backup of `server A` on `server B`.
1. **_Warning:_** Ensure `server B` is a clean SystemLink installation, any existing data will be deleted.
1. Follow the restore instructions to restore the backed up data onto `server B`.

# Development
See `CONTRIBUTING.MD` for detailed instructions on developing, testing, and releasing the tool.

# Supported Services
The services that can be migrated with this utility along with short descriptions can be listed by running:
```bash
nislmigrate capture -h
```

Most services require migrating the `--security` service at the same time for the migration to be successful, and some services have additional dependencies which are listed in the table below.  

| **Supported Service**                     | **Argument Flag** | **Also requires migrating** | **Additional Notes**                                                                                                                                                                                                                                                                                                                                                                             |
|---------------------------------|-------------------|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Security                        | `--security`      |                             |                                                                                                                                                                                                                                                                                                                                                                                                  |
| User Data                       | `--userdata`      | `--security`                |                                                                                                                                                                                                                                                                                                                                                                                                  |
| Notifications                   | `--notification`  | `--security`                |                                                                                                                                                                                                                                                                                                                                                                                                  |
| File Ingestion                  | `--files`         | `--security`                | - Must migrate file to the same storage location on the new System Link server.<br>- To capture/restore only the database but not the files themselves, use `--files --files-metadata-only`. This could be useful if, for example, files are stored on a file server with separate backup.<br>- If files are stored in Amazon Simple Storage Service (S3), use `--files --files-metadata-only`.<br>- If the file store path is different on the server you are restoring to, use the '--change-file-store-root [NEW_ROOT]' flag to update the metadata during a restore operation.   |
| Repository                      | `--repo`          | `--security`                | - Feeds may require additional updates if servers used for migration have different domain names                                                                                                                                                                                                                                                                                                 |
| Dashboards and Web Applications | `--dashboards`    | `--security`                |                                                                                                                                                                                                                                                                                                                                                                                                  |
| System States                   | `--systemstates`  | `--security`                | - Feeds may require additional updates if servers used for migration have different domain names<br>- Cannot be migrated between 2020R1 and 2020R2 servers                                                                                                                                                                                                                                       |
| Tag Ingestion and Tag History   | `--tags`          | `--security`                |                                                                                                                                                                                                                                                                                                                                                                                                  |
| Tag Alarm Rules                 | `--tagrule`       | `--security`<br>`--notification` |                                                                                                                                                                                                                                                                                                                                                                                                  |
| Alarm Instances                 | `--alarms`        | `--security`<br>`--notification` | - Cannot be migrated between 2020R1 and 2020R2 servers                                                                                                                                                                                                                                                                                                                                           |
| Asset Alarm Rules               | `--assetrule`     | `--security`<br>`--notification` |                                                                                                                                                                                                                                                                                                                                                                                                  |
| Asset Management                | `--assets`        | `--security`<br>`--files`<br>`--tags`        |                                                                                                                                                                                                                                                                                                                                                                                                  |
| Test Monitor                    | `--tests`         | `--security`<br>`--file`         |                                                                                                                                                                                                                                                                                                                                                                                                  |
| Systems                         | `--systems`       | `--security`<br>`--tags`<br>`--file`  | - _WARNING:_ Captured systems data contains encrypted secret information and should not be copied to a publicly accessible location.<br>- To capture/restore systems, a secret must be provided using the `--secret <SECRET>` command line flag. Captured systems data will require the same secret to be provided as was provided during capture in order to be able to decrypt sensitive data. |

There are plans to support the following services in the future:
- OPC UA Client: `--opc`
- TDM `--tdm`
- Cloud Connector `--cloud`
