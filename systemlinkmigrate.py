# Generic migration utility for migrating various data and settings between SystemLink servers. 
# Not all services will be supported. Addtional services will be supported over time. 

import os, json, shutil, subprocess, argparse, sys
# from slmigrate.migrate import restore
# from slmigrate.migrate import capture
# import migrate
# from slmigrate.migrate import restore

# This will makes test work, but the script will fail. 
# from slmigrate.migrate import restore
# from slmigrate.migrate import capture

# This will make the app work but test will fail. 
# from migrate import restore
# from migrate import capture

from slmigrate.migrate import capture
from slmigrate.migrate import restore

# Global Constants
migration_dir = os.path.join(os.path.abspath(os.sep), "migration")
no_sql_dump_dir = os.path.join(migration_dir, "mongo-dump")
# program_file_dir = os.environ.get("ProgramW6432")
# program_data_dir = os.environ.get("ProgramData")
# fis_data_source_dir = os.path.join(program_data_dir, "National Instruments", "Skyline", "Data", "FileIngestion")
# fis_data_migration_dir = os.path.join(migration_dir, "FileIngestion")
# mongo_dump = os.path.join(program_file_dir, "National Instruments", "Shared", "Skyline", "NoSqlDatabase", "bin", "mongodump.exe")

#Service name strings
tagservice = "TagIngestion"
opcservice = "OpcClient"

# Setup available command line arguments
def parse_arguments(args):
    parser = argparse.ArgumentParser()
    parser.add_argument ("--capture", help="capture is used to pull data and settings off SystemLink server", action="store_true", )
    parser.add_argument ("--restore", help="restore is used to push data and settings to a clean SystemLink server. ", action="store_true", )
    parser.add_argument ("--tag", "--tags", "--tagingestion", "--taghistory", help="Migrate tags and tag histories", action="store_true", )
    parser.add_argument ("--opc", "--opcua", "--opcuaclient", help="Migrate OPCUA sessions and certificates", action="store_true")
    return  parser 

def add_numbers(num1, num2):
    sum = num1 + num2
    return sum

# Main
if __name__ == "__main__":
    arguments = parse_arguments(sys.argv[1:]).parse_args()
    if not(arguments.capture) and not(arguments.restore):
        print("Please use --capture or --restore to determine which direction the migration is occuring. ")
    if arguments.capture and arguments.restore:
        print("You cannot use --capture and --restore simultaneously. ")
    if arguments.tag:
        if arguments.capture:
            capture.capture_migration(tagservice)
        if arguments.restore:
            restore.restore_migration(tagservice)
    if arguments.opc:
        if arguments.capture:
            capture.capture_migration(opcservice)
        if arguments.restore:
            restore.restore_migration(opcservice)


        