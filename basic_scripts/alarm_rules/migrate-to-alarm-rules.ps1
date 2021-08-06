# migrate-to-alarm-rules.ps1

# This example will migrate all tag alarm rules generated from running migrate-from-alarms.ps1 to another SystemLink Server
# This script does not migrate tags associated with alarms, or  the alarm instances generated from these rule. 

# Set variables for various paths used during migration
$MigrationDir = "C:\migration"
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$MongoRestore = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NoSqlDatabase bin mongorestore.exe

# Import MongoDB dump files 
$Service = "TagRuleEngine"
$ConfigFile = Join-Path $env:ProgramData "National Instruments" Skyline Config "$Service.json"
$Config = (Get-Content $ConfigFile | ConvertFrom-Json).$Service
$DumpFile = Join-Path $NoSqlDumpDir $Config."Mongo.Database"
. $MongoRestore --port $Config."Mongo.Port" --db $Config."Mongo.Database" --username $Config."Mongo.User" --password $Config."Mongo.Password" --gzip $DumpFile

#Restart SystemLink services
. $SlConfCmd stop-all services wait
. $SlConfCmd start-all-services