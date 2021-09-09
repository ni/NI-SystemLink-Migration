"""Test constants."""

import os
from types import SimpleNamespace

root_dir = os.path.abspath(os.sep)

mongod_exe = os.path.join(root_dir, 'MongoDB', 'bin', 'mongod.exe')
mongo_config = os.path.join(os.getcwd(), 'test', 'testmongo.conf')
mongo_dump = os.path.join(root_dir, 'MongoDB', 'bin', 'mongodump.exe')
mongo_restore = os.path.join(root_dir, 'MongoDB', 'bin', 'mongod.exe', 'mongorestore.exe')
service_config_dir = os.path.join(os.getcwd(), 'test')
migration_dir = os.path.join(os.path.abspath(os.sep), 'migration_test')

test_dict = {
    'arg': 'test_service',
    'name': 'local',
    'directory_migration': True,
    'singlefile_migration': True,
    'require_service_restart': False,
    'singlefile_migration_dir': os.path.join(os.path.abspath(os.sep), 'migration_test'),
    'singlefile_source_dir': os.path.join(os.path.abspath(os.sep), 'source_test_dir'),
    'singlefile_to_migrate': os.path.join(
        os.path.abspath(os.sep), 'source_test_dir', 'demofile2.txt'
    ),
    'migration_dir': os.path.join(migration_dir, 'local'),
    'source_dir': os.path.join(os.path.abspath(os.sep), 'source_test_dir'),
}
test_service = SimpleNamespace(**test_dict)
