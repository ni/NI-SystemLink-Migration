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
mongo_dump_cmd = mongo_dump
mongo_dump_cmd += " --port " + str(config[SERVICE]["Mongo.Port"])
mongo_dump_cmd += " --db " + config[SERVICE]["Mongo.Database"]
mongo_dump_cmd += " --username " + config[SERVICE]["Mongo.User"]
mongo_dump_cmd += " --password " + config[SERVICE]["Mongo.Password"]
mongo_dump_cmd += " --out " + no_sql_dump_dir
mongo_dump_cmd += " --gzip"
subprocess.run(mongo_dump_cmd)
