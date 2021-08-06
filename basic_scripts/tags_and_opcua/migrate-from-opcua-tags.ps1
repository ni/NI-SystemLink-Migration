# migrate-from-opcua-tags.ps1

# This example will generate a migration directory container all tags, tag histories, OPCUA sessions, and OPCUA certificates on the SystemLink Server.  
# This script will migrate all tags, not just those created by OPCUA session monitors. 

# Set variables for various paths used during migration
$MigrationDir = "C:\migration"
$OpcMigrationDir = Join-Path $MigrationDir OpcClient
$NoSqlDumpDir = Join-Path $MigrationDir mongo-dump
$OpcCertSourceDir = Join-Path $env:ProgramData "National Instruments" Skyline Data OpcClient
$OpcCertMigrationDir = Join-Path $MigrationDir OpcClient 
$keyValueDbMigrationDir = Join-Path $MigrationDir keyvaluedb
$KeyValueDbDumpSource = Join-Path $env:ProgramData "National Instruments" Skyline KeyValueDatabase dump.rdb
$MongoDump = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NoSqlDatabase bin mongodump.exe
$SlConfCmd = Join-Path $env:ProgramFiles "National Instruments" Shared Skyline NISystemLinkServerConfigCmd.exe

# Dump mongodb to migration directory for OPCUA and Tag Historian
$Service = "OpcClient"
For ($i=0; $i -lt 2; $i++) {
    $ConfigFile = Join-Path $env:ProgramData "National Instruments" Skyline Config "$Service.json"
    $Config = (Get-Content $ConfigFile | ConvertFrom-Json).$Service

    . $MongoDump --port $Config."Mongo.Port" --db $Config."Mongo.Database" --username $Config."Mongo.User" --password $Config."Mongo.Password" --out $NoSqlDumpDir --gzip
    $Service = "TagHistorian"
}

# Stop SystemLink services to dump Redis DB contents to disk and dump to migration directory
Write-Host "Stopping all SystemLink services..."
. $SlConfCmd stop-all-services
New-Item -ItemType directory -Path $keyValueDbMigrationDir 
Copy-Item $KeyValueDbDumpSource -Destination $keyValueDbMigrationDir -Verbose

# Copy OPCUA certificats to migration directory
Copy-Item $OpcCertSourceDir -Destination $OpcCertMigrationDir -Recurse -Verbose

# Restart SystemLink services
Write-Host "Starting all SystemLink services..."
. $SlConfCmd start-all-services