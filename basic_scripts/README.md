# Basic Migration Scripts
This directory contains multiple PowerShell and Python scripts to migrate SystemLink data. These simple examples are receiving no new updates. Using `systemlinkmigrate.py` is recommended and is receiving active development.

## Migrating  with Python
- These scripts require >=Python3 to run. Installers can be found at [python.org](https://www.python.org/downloads/)
- The documentation in this repo assumes Python has been added to your PATH variable. 
- Depending on the setup of your environment you may invoke python with `python`, `python3`, or `py`. Documentation in this repo use `py`. 

## Migrating with PowerShell
- These scripts require PowerShell 7 to run. Installers can be found in the [Powershell Github repo](https://github.com/PowerShell/PowerShell/releases). 
- PowerShell must be run as an administrator. 
- The Powershell `Set-ExecutionPolicy` cmdlet may have to be modified to run Powershell scripts. See [SetExecution-Policy](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7]) for more details on modifying this setting. 

## Basic Migration Pattern
These scripts use `mongodump` and `mongorestore` commands, and file copies to orchestrate migration of various data and settings in SystemLink. This pattern can be extended to cover additional aspects of SystemLink. The current set of scripts demonstrate the migration of subsets of the overall data ingested by SystemLink, but each script can be used sequentially to dump more data into the `migration` directory. 

- **Migrate OPCUA, Tags, and Tag History**: This example will migrate all tags, tag histories, OPCUA sessions and certificates. 
- **Migrate Test Results and Test Steps**: This example will migrate test results and test step data. 
- **Migrate Tag Alarm Rule**: This example will migrate tag alarms rules. This includes the default tag alarm rules created when SystemLink is installed. Note this may lead to duplicate rules in the new server. 
- **Migrate Ingested Files**: This example will migrate files uploaded via the File Ingestion service to a new a SystemLink server 

## Python 
### Migrating From an Existing Server
1. Read and understand the [prerequisites](https://github.com/prestwick/systemlink-migration-sandbox/blob/master/README.md#Prerequisites) for this script. 
2. Clone or download this repository
3. Open a cmd or PowerShell window in the directory location of this script
4. Run `py migrate-from-alarm-rules.py` (or similar for a different service)
5. Copy the `C:\migration` directory created another SystemLink server.

### Migrating To a New Server
1. Copy the `migration` directory creating by executing the **Migrating From an Existing Server** steps to `C:\` of the new SystemLink server. 
2. Clone or download this repository
3. Open a cmd or PowerShell window in the directory location of this script
4. Run `py migrate-to-alarm-rules.py` (or similar for a different service)

## PowerShell
### Migrating From an Existing Server
1. Read and understand the [prerequisites](https://github.com/prestwick/systemlink-migration-sandbox/blob/master/README.md#Prerequisites) for this script. 
2. Clone or download this repository
3. Open a PowerShell window in the directory location of this script
4. Run `\.migrate-from-alarms-rules.ps1` (or similar for a different service)
5. Copy the `C:\migration` directory created another SystemLink server. 

### Migrating To a New Server
1. Copy the `migration` directory creating by executing the **Migrating From an Existing Server** steps to `C:\` of the new SystemLink server. 
2. Clone or download this repository
3. Open a PowerShell window in the directory location of this script
4. Run `\.migrate-to-alarms-rules.ps1` (or similar for a different service)