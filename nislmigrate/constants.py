"""Application constants."""

import os
from types import SimpleNamespace

# Global Path Constants
# TODO: Move this to argument_handler. All paths should be relative and combined with the correct base migration directory by plugins.
DEFAULT_MIGRATION_DIRECTORY = os.path.expanduser("~\\Documents\\migration")
MONGO_MIGRATION_SUB_DIRECTORY = os.path.join(DEFAULT_MIGRATION_DIRECTORY, "mongo-dump")
program_file_dir = os.environ.get("ProgramW6432")
program_data_dir = os.environ.get("ProgramData")

# Variables for calling EXEs
mongo_dump = os.path.join(
    program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NoSqlDatabase",
    "bin",
    "mongodump.exe",
)
mongo_restore = os.path.join(
    program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NoSqlDatabase",
    "bin",
    "mongorestore.exe",
)
mongod_exe = os.path.join(
    program_file_dir,
    "National Instruments",
    "Shared",
    "Skyline",
    "NoSqlDatabase",
    "bin",
    "mongod.exe",
)
mongo_config = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "NoSqlDatabase", "mongodb.conf"
)

service_config_dir = config_file = os.path.join(
    program_data_dir, "National Instruments", "Skyline", "Config"
)

# Global constants for argparse
MIGRATION_ACTION_FIELD_NAME = "action"

# Service Dictionaries
tag_dict = {
    "arg": "tag",
    "name": "TagHistorian",
    "directory_migration": False,
    "singlefile_migration": True,
    "singlefile_migration_dir": os.path.join(DEFAULT_MIGRATION_DIRECTORY, "keyvaluedb"),
    "singlefile_source_dir": os.path.join(
        program_data_dir, "National Instruments", "Skyline", "KeyValueDatabase"
    ),
    "singlefile_to_migrate": "dump.rdb",
}
tag = SimpleNamespace(**tag_dict)

opc_dict = {
    "arg": "opc",
    "name": "OpcClient",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": os.path.join(DEFAULT_MIGRATION_DIRECTORY, "OpcClient"),
    "source_dir": os.path.join(
        program_data_dir, "National Instruments", "Skyline", "Data", "OpcClient"
    ),
}
opc = SimpleNamespace(**opc_dict)

fis_dict = {
    "arg": "fis",
    "name": "FileIngestion",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": os.path.join(DEFAULT_MIGRATION_DIRECTORY, "FileIngestion"),
    "source_dir": os.path.join(
        program_data_dir, "National Instruments", "Skyline", "Data", "FileIngestion"
    ),
}
fis = SimpleNamespace(**fis_dict)

testmonitor_dict = {
    "arg": "testmonitor",
    "name": "TestMonitor",
    "directory_migration": False,
    "singlefile_migration": False,
}
testmonitor = SimpleNamespace(**testmonitor_dict)

alarmrule_dict = {
    "arg": "alarmrule",
    "name": "TagRuleEngine",
    "directory_migration": False,
    "singlefile_migration": False,
}
alarmrule = SimpleNamespace(**alarmrule_dict)

asset_dict = {
    "arg": "asset",
    "name": "AssetPerformanceManagement",
    "directory_migration": False,
    "singlefile_migration": False,
}
asset = SimpleNamespace(**asset_dict)

repository_dict = {
    "arg": "repository",
    "name": "Repository",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": os.path.join(DEFAULT_MIGRATION_DIRECTORY, "Respository"),
    "source_dir": os.path.join(
        program_file_dir,
        "National Instruments",
        "Shared",
        "Web Services",
        "NI",
        "repo_webservice",
        "files",
    ),
}
repository = SimpleNamespace(**repository_dict)

userdata_dict = {
    "arg": "userdata",
    "name": "UserData",
    "directory_migration": False,
    "singlefile_migration": False,
}
userdata = SimpleNamespace(**userdata_dict)

notification_dict = {
    "arg": "notification",
    "name": "Notification",
    "directory_migration": False,
    "singlefile_migration": False,
}
notification = SimpleNamespace(**notification_dict)

states_dict = {
    "arg": "states",
    "name": "SystemsStateManager",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": os.path.join(DEFAULT_MIGRATION_DIRECTORY, "SystemsStateManager"),
    "source_dir": os.path.join(
        program_data_dir,
        "National Instruments",
        "Skyline",
        "Data",
        "SystemsStateManager",
    ),
}
states = SimpleNamespace(**states_dict)

no_sql_dict = {"name": "NoSqlDatabase"}
no_sql = SimpleNamespace(**no_sql_dict)

thdbbug_dict = {
    "arg": "thdbbug",
    "name": "TagHistorian",
    "directory_migration": False,
    "singlefile_migration": False,
    "intradb_migration": True,
    "collections_to_migrate": ["metadata", "values"],
    "source_db": "admin",
    "destination_db": "nitaghistorian",
}
thdbbug = SimpleNamespace(**thdbbug_dict)
