import os

opc_dict = {
    "arg": "opc",
    "name": "OpcClient",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "OpcClient",
    "source_dir": os.path.join(
        os.environ.get("ProgramData"), "National Instruments", "Skyline", "Data", "OpcClient"
    ),
}

fis_dict = {
    "arg": "fis",
    "name": "FileIngestion",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "FileIngestion",
    "source_dir": os.path.join(
        os.environ.get("ProgramData"), "National Instruments", "Skyline", "Data", "FileIngestion"
    ),
}

testmonitor_dict = {
    "arg": "testmonitor",
    "name": "TestMonitor",
    "directory_migration": False,
    "singlefile_migration": False,
}

alarmrule_dict = {
    "arg": "alarmrule",
    "name": "TagRuleEngine",
    "directory_migration": False,
    "singlefile_migration": False,
}

asset_dict = {
    "arg": "asset",
    "name": "AssetPerformanceManagement",
    "directory_migration": False,
    "singlefile_migration": False,
}

repository_dict = {
    "arg": "repository",
    "name": "Repository",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "Respository",
    "source_dir": os.path.join(
        os.environ.get("ProgramW6432"),
        "National Instruments",
        "Shared",
        "Web Services",
        "NI",
        "repo_webservice",
        "files",
    ),
}

userdata_dict = {
    "arg": "userdata",
    "name": "UserData",
    "directory_migration": False,
    "singlefile_migration": False,
}

notification_dict = {
    "arg": "notification",
    "name": "Notification",
    "directory_migration": False,
    "singlefile_migration": False,
}

states_dict = {
    "arg": "states",
    "name": "SystemsStateManager",
    "directory_migration": True,
    "singlefile_migration": False,
    "migration_dir": "SystemsStateManager",
    "source_dir": os.path.join(
        os.environ.get("ProgramData"),
        "National Instruments",
        "Skyline",
        "Data",
        "SystemsStateManager",
    ),
}

no_sql_dict = {"name": "NoSqlDatabase"}

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
