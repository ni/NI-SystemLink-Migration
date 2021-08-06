# migrate-to-test-data.ps1

# This example will migrate all test results generated from running migrate-from-test-data.ps1 to another SystemLink Server
# This script will not migrate file attached to test results 

# Set variables for various paths used during migration
$MigrationDir = "C:\migration"
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$MongoRestore = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NoSqlDatabase bin mongorestore.exe

# Import MongoDB dump files 
$Service = "TestMonitor"
$ConfigFile = Join-Path $env:ProgramData "National Instruments" Skyline Config "$Service.json"
$Config = (Get-Content $ConfigFile | ConvertFrom-Json).$Service
$DumpFile = Join-Path $NoSqlDumpDir $Config."Mongo.Database"
. $MongoRestore --port $Config."Mongo.Port" --db $Config."Mongo.Database" --username $Config."Mongo.User" --password $Config."Mongo.Password" --gzip $DumpFile