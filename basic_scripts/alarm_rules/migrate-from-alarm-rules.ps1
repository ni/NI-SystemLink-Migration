# migrate-from-alarm-rules.ps1

# This example will generate a migration directory containing all the tag alarm rules within a SystemLink server. 
# This script does not migrate tags associated with alarms, or  the alarm instances generated from these rule. 

# Set variables for various paths used during migration
$MigrationDir = "C:\migration"
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$MongoDump = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NoSqlDatabase bin mongodump.exe

# Dump mongodb to migration directory
$Service = "TagRuleEngine"
$ConfigFile = Join-Path $env:ProgramData "National Instruments" Skyline Config "$Service.json"
$Config = (Get-Content $ConfigFile | ConvertFrom-Json).$Service
. $MongoDump --port $Config."Mongo.Port" --db $Config."Mongo.Database" --username $Config."Mongo.User" --password $Config."Mongo.Password" --out $NoSqlDumpDir --gzip
