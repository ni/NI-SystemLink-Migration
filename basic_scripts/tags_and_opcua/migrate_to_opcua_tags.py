"""Example script.

This example will migrate all tags, tag histories, OPCUA session, and OPCUA certificates generated
 from running migrate-from-opcua-tags.ps1 to another SystemLink Server.

 This script will migrate all tags, not just those created by OPCUA session monitors.
"""

import json
import os
import shutil
import subprocess

# Set variables for various paths used during migration
MIGRATION_DIR = r"C:\migration"
no_sql_dump_dir = os.path.join(MIGRATION_DIR, "mongo-dump")
program_file_dir = os.environ.get("ProgramW6432")
program_data_dir = os.environ.get("ProgramData")
sl_data_dir = os.path.join(program_data_dir, "National Instruments", "Skyline", "Data")
opc_cert_source_dir = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Data", "OpcClient"
)
opc_cert_migration_dir = os.path.join(MIGRATION_DIR, "OpcClient")
keyvaluedb_migration_dir = os.path.join(MIGRATION_DIR, "keyvaluedb")
keyvaluedb_dump_dir = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "KeyValueDatabase"
)
keyvaluedb_dump = os.path.join(keyvaluedb_migration_dir, "dump.rdb")
mongo_restore = os.path.join(
    program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NoSqlDatabase",
    "bin",
    "mongorestore.exe",
)
slconf_cmd = os.path.join(
    program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NISystemLinkServerConfigCmd.exe",
)
slconf_cmd_stop = slconf_cmd + " stop-all-services" + " wait"
slconf_cmd_start = slconf_cmd + " start-all-services"

# Import MongoDB dump files
services = ["OpcClient", "TagHistorian"]
for service in services:
    # Get data from service's json config file
    config_file = os.path.join(
        program_data_dir, "National Instruments", "Skyline", "Config", service + ".json"
    )
    with open(config_file, encoding="utf-8-sig") as json_file:
        config = json.load(json_file)

    # Restore mongo database from contents of migration directory
    mongo_dump_file = os.path.join(no_sql_dump_dir, config[service]["Mongo.Database"])
    mongo_restore_cmd = mongo_restore
    mongo_restore_cmd += " --port " + str(config[service]["Mongo.Port"])
    mongo_restore_cmd += " --db " + config[service]["Mongo.Database"]
    mongo_restore_cmd += " --username " + config[service]["Mongo.User"]
    mongo_restore_cmd += " --password " + config[service]["Mongo.Password"]
    mongo_restore_cmd += " --gzip " + mongo_dump_file

    subprocess.run(mongo_restore_cmd, check=True)

# Stop SystemLink services to dump Redis DB contents to disk and dump to migration directory
print("Stopping all SystemLink services")
subprocess.run(slconf_cmd_stop, check=True)

# Replace the contents of the current Redis DB instance. This will remove previously created
# tags from the server.
shutil.copy(keyvaluedb_dump, keyvaluedb_dump_dir)

# Copy OPCUA certificates to data directory
shutil.rmtree(opc_cert_source_dir)
shutil.copytree(opc_cert_migration_dir, opc_cert_source_dir)

# Restart SystemLink services
print("Starting all SystemLink services...")
subprocess.run(slconf_cmd_start, check=True)
