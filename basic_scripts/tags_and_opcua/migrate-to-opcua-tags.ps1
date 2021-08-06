# migrate-to-opcua-tags.ps1

# This example will migrate all tags, tag histories, OPCUA session, and OPCUA certificates generated from running migrate-from-opcua-tags.ps1 to another SystemLink Server
# This script will migrate all tags, not just those created by OPCUA session monitors. 

# Set variables for various paths used during migration
$MigrationDir = "C:\migration"
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$OpcCertMigrationDir = Join-Path $MigrationDir OpcClient 
$keyValueDbMigrationDir = Join-Path $MigrationDir keyvaluedb
$MongoRestore = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NoSqlDatabase bin mongorestore.exe
$SlConfCmd = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NISystemLinkServerConfigCmd.exe
$KeyValueDbMigrationDump = Join-Path $KeyValueDbMigrationDir dump.rdb
$KeyValueDbDir = Join-Path $env:ProgramData "National Instruments" Skyline KeyValueDatabase
$SlDataDir = Join-Path $env:ProgramData "National Instruments Skyline Data"

# Import MongoDB dump files 
$Service = "OpcClient"
For ($i=0; $i -lt 2; $i++) {
    $ConfigFile = Join-Path $env:ProgramData "National Instruments" Skyline Config "$Service.json"
    $Config = (Get-Content $ConfigFile | ConvertFrom-Json).$Service
    $DumpFile = Join-Path $NoSqlDumpDir $Config."Mongo.Database"

    . $MongoRestore --port $Config."Mongo.Port" --db $Config."Mongo.Database" --username $Config."Mongo.User" --password $Config."Mongo.Password" --gzip $DumpFile
    $Service = "TagHistorian"
}

# Replace the contents of the current Redis DB instance. This will remove previously created tags from the server. 
Write-Host "Stopping all SystemLink services..."
. $SlConfCmd stop-all-services
Copy-Item $KeyValueDbMigrationDump -Destination $KeyValueDbDir

# Copy OPCUA certificates to new server
Copy-Item $OpcCertMigrationDir -Destination $SlDataDir -Recurse -force

# Restart SystemLink services
Write-Host "Starting all SystemLink services..."
. $SlConfCmd start-all-services