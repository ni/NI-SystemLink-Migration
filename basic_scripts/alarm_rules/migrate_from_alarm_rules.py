"""Example script.

This example will generate a migration directory containing all the tag alarm_rules within a
SystemLink server.

This script does not migrate tags associated with alarms, or  the alarm instances generated from
these rule.
"""

import json
import os
import subprocess

# Set variables for various paths used during migration
MIGRATION_DIRECTORY = r"C:\migration"
no_sql_dump_dir = os.path.join(MIGRATION_DIRECTORY, "mongo-dump")
program_file_dir = os.environ.get("ProgramW6432")
program_data_dir = os.environ.get("ProgramData")
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
SERVICE = "TagRuleEngine"
config_file = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Config", SERVICE + ".json"
)
with open(config_file, encoding="utf-8-sig") as json_file:
    config = json.load(json_file)

# Dump mongo database to migration directory
mongo_dump_cmd = (
    mongo_dump
    + " --port "
    + str(config[SERVICE]["Mongo.Port"])
    + " --db "
    + config[SERVICE]["Mongo.Database"]
    + " --username "
    + config[SERVICE]["Mongo.User"]
    + " --password "
    + config[SERVICE]["Mongo.Password"]
    + " --out "
    + no_sql_dump_dir
    + " --gzip"
)
subprocess.run(mongo_dump_cmd)
