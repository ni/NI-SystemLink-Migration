# migrate-from-fis.ps1

# This example will generate a migration directory containing all file ingested by a SystemLink Server.  

# Set variables for various paths used during migration
$MigrationDir = "C:\migration"
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$FisDataSourceDir = Join-Path $env:ProgramData "National Instruments" Skyline Data FileIngestion
$FisDataMigrationDir = Join-Path $MigrationDir FileIngestion
$MongoDump = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NoSqlDatabase bin mongodump.exe

# Dump mongodb to migration directory for OPCUA and Tag Historian
$Service = "FileIngestion"
$ConfigFile = Join-Path $env:ProgramData "National Instruments" Skyline Config "$Service.json"
$Config = (Get-Content $ConfigFile | ConvertFrom-Json).$Service
. $MongoDump --port $Config."Mongo.Port" --db $Config."Mongo.Database" --username $Config."Mongo.User" --password $Config."Mongo.Password" --out $NoSqlDumpDir --gzip

# Copy ingested files to the migration directory
Copy-Item $FisDataSourceDir -Destination $MigrationDir -Recurse -Verbose