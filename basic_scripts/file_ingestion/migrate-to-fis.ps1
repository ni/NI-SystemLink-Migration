# migrate-from-fis.ps1

# This example will migrate all ingested file data to a new SystemLink server

# Set variables for various paths used during migration
$MigrationDir = "C:\migration"
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$FisDataSourceDir = Join-Path $env:ProgramData "National Instruments" Skyline Data FileIngestion
$FisDataMigrationDir = Join-Path $MigrationDir FileIngestion
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$MongoRestore = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NoSqlDatabase bin mongorestore.exe
$SlDataDir = Join-Path $env:ProgramData "National Instruments" Skyline Data

# Import MongoDB dump files 
$Service = "FileIngestion"

$ConfigFile = Join-Path $env:ProgramData "National Instruments" Skyline Config "$Service.json"
$Config = (Get-Content $ConfigFile | ConvertFrom-Json).$Service
$DumpFile = Join-Path $NoSqlDumpDir $Config."Mongo.Database"
. $MongoRestore --port $Config."Mongo.Port" --db $Config."Mongo.Database" --username $Config."Mongo.User" --password $Config."Mongo.Password" --gzip $DumpFile

# Copy ingested files to new server
Copy-Item $FisDataMigrationDir -Destination $SlDataDir -Recurse -force