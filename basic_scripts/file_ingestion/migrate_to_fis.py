"""Example script.

This example will migrate all ingested file data to a new SystemLink server.
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
fis_data_source_dir = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Data", "FileIngestion"
)
fis_data_migration_dir = os.path.join(MIGRATION_DIR, "FileIngestion")
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
SERVICE = "FileIngestion"
config_file = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Config", SERVICE + ".json"
)
with open(config_file, encoding="utf-8-sig") as json_file:
    config = json.load(json_file)

# Restore mongo database from contents of migration directory
mongo_dump_file = os.path.join(no_sql_dump_dir, config[SERVICE]["Mongo.Database"])
mongo_restore_cmd = (
    mongo_restore
    + " --port "
    + str(config[SERVICE]["Mongo.Port"])
    + " --db "
    + config[SERVICE]["Mongo.Database"]
    + " --username "
    + config[SERVICE]["Mongo.User"]
    + " --password "
    + config[SERVICE]["Mongo.Password"]
    + " --gzip "
    + mongo_dump_file
)
subprocess.run(mongo_restore_cmd)

# Copy file from migration directory to data directory
migration_files = os.listdir(fis_data_migration_dir)
for file_name in migration_files:
    full_file_path = os.path.join(fis_data_migration_dir, file_name)
    if os.path.isfile(full_file_path):
        shutil.copy(full_file_path, fis_data_source_dir)
