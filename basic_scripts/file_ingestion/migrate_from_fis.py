"""Example script.

This example will generate a migration directory containing all file ingested by a
SystemLink Server.
"""

import json
import os
import shutil
import subprocess

# Set variables for various paths used during migration
migration_dir = r"C:\migration"
no_sql_dump_dir = os.path.join(migration_dir, "mongo-dump")
program_file_dir = os.environ.get("ProgramW6432")
program_data_dir = os.environ.get("ProgramData")
fis_data_source_dir = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Data", "FileIngestion"
)
fis_data_migration_dir = os.path.join(migration_dir, "FileIngestion")
mongo_dump = os.path.join(
    program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NoSqlDatabase",
    "bin",
    "mongodump.exe",
)

# Get data from service's json config file
service = "FileIngestion"
config_file = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Config", service + ".json"
)
with open(config_file, encoding="utf-8-sig") as json_file:
    config = json.load(json_file)

# Dump mongo database to migration directory
mongo_dump_cmd = mongo_dump
mongo_dump_cmd += " --port " + str(config[service]["Mongo.Port"])
mongo_dump_cmd += " --db " + config[service]["Mongo.Database"]
mongo_dump_cmd += " --username " + config[service]["Mongo.User"]
mongo_dump_cmd += " --password " + config[service]["Mongo.Password"]
mongo_dump_cmd += " --out " + no_sql_dump_dir
mongo_dump_cmd += " --gzip"
subprocess.run(mongo_dump_cmd)

# Copy ingested files to migration direction
os.mkdir(fis_data_migration_dir)
migration_files = os.listdir(fis_data_source_dir)
for file_name in migration_files:
    full_file_path = os.path.join(fis_data_source_dir, file_name)
    if os.path.isfile(full_file_path):
        shutil.copy(full_file_path, fis_data_migration_dir)
