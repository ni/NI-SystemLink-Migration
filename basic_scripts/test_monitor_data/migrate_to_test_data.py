"""Example script.

This example will migrate all test results generated from running migrate-from-test-data.ps1 to
another SystemLink Server

This script will not migrate file attached to test results.
"""

import json
import os
import subprocess

# Set variables for various paths used during migration
MIGRATION_DIRECTORY = r"C:\migration"
no_sql_dump_dir = os.path.join(MIGRATION_DIRECTORY, "mongo-dump")
program_file_dir = os.environ.get("ProgramW6432")
program_data_dir = os.environ.get("ProgramData")
mongo_restore = os.path.join(
    program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NoSqlDatabase",
    "bin",
    "mongorestore.exe",
)

# Get data from service's json config file
SERVICE = "TestMonitor"
config_file = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Config", SERVICE + ".json"
)
with open(config_file, encoding="utf-8-sig") as json_file:
    config = json.load(json_file)

# Restore mongo database from contents of migration directory
mongo_dump_file = os.path.join(no_sql_dump_dir, config[SERVICE]["Mongo.Database"])
mongo_restore_cmd = mongo_restore
mongo_restore_cmd += " --port " + str(config[SERVICE]["Mongo.Port"])
mongo_restore_cmd += " --db " + config[SERVICE]["Mongo.Database"]
mongo_restore_cmd += " --username " + config[SERVICE]["Mongo.User"]
mongo_restore_cmd += " --password " + config[SERVICE]["Mongo.Password"]
mongo_restore_cmd += " --gzip " + mongo_dump_file

subprocess.run(mongo_restore_cmd, check=True)
