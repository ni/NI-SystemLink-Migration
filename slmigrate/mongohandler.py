"""Handle Mongo operations."""

import json
import os
import subprocess
import sys
from types import SimpleNamespace

import bson
from pymongo import errors as pyerr
from pymongo import MongoClient

from slmigrate import constants


def get_service_config(service):
    """TODO: Complete documentation.

    :param service:
    :return:
    """
    config_file = os.path.join(constants.service_config_dir, service.name + ".json")
    with open(config_file, encoding="utf-8-sig") as json_file:
        return json.load(json_file)


def start_mongo(mongod_exe, mongo_config):
    """TODO: Complete documentation.

    :param mongod_exe:
    :param mongo_config:
    :return:
    """
    mongo_process = subprocess.Popen(
        mongod_exe + " --config " + '"' + str(mongo_config) + '"',
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        env=os.environ,
    )
    return mongo_process


def stop_mongo(proc):
    """TODO: Complete documentation.

    :param proc:
    :return:
    """
    subprocess.Popen.kill(proc)


def capture_migration(service):
    """TODO: Complete documentation.

    :param service:
    :return:
    """
    # TODO get rid of the [service.name] by changing the property
    cmd_to_run = (
        constants.mongo_dump
        + " --port "
        + str(service.config[service.name]["Mongo.Port"])
        + " --db "
        + service.config[service.name]["Mongo.Database"]
        + " --username "
        + service.config[service.name]["Mongo.User"]
        + " --password "
        + service.config[service.name]["Mongo.Password"]
        + " --out "
        + constants.mongo_migration_dir
        + " --gzip"
    )
    subprocess.run(cmd_to_run, check=True)


def restore_migration(service):
    """TODO: Complete documentation.

    :param service:
    :return:
    """

    config = service.config
    mongo_dump_file = os.path.join(
        constants.mongo_migration_dir, config[service.name]["Mongo.Database"]
    )
    cmd_to_run = (
        constants.mongo_restore
        + " --port "
        + str(config[service.name]["Mongo.Port"])
        + " --db "
        + config[service.name]["Mongo.Database"]
        + " --username "
        + config[service.name]["Mongo.User"]
        + " --password "
        + config[service.name]["Mongo.Password"]
        + " --gzip "
        + mongo_dump_file
    )
    subprocess.run(cmd_to_run, check=True)


def migrate_document(destination_collection, document):
    """TODO: Complete documentation.

    :param destination_collection:
    :param document:
    :return:
    """
    try:
        print("Migrating " + str(document["_id"]))
        destination_collection.insert_one(document)
    except pyerr.DuplicateKeyError:
        print("Document " + str(document["_id"]) + " already exists. Skipping")


def identify_metadata_conflict(destination_collection, source_document):
    """TODO: Complete documentation.

    :param destination_collection:
    :param source_document:
    :return:
    """
    destination_query = {
        "$and": [
            {"workspace": source_document["workspace"]},
            {"path": source_document["path"]},
        ]
    }
    destination_document = destination_collection.find_one(destination_query)
    if destination_document:
        return SimpleNamespace(
            **{
                "source_id": source_document["_id"],
                "destination_id": destination_document["_id"],
            }
        )

    return None


def merge_history_document(source_id, destination_id, destination_db):
    """TODO: Complete documentation.

    :param source_id:
    :param destination_id:
    :param destination_db:
    :return:
    """
    destination_collection = destination_db.get_collection("values")
    destination_collection.update_one(
        {"metadataId": source_id}, {"$set": {"metadataId": destination_id}}
    )


def migrate_metadata_collection(source_db, destination_db):
    """TODO: Complete documentation.

    :param source_db:
    :param destination_db:
    :return:
    """
    collection_name = "metadata"
    source_collection = source_db.get_collection(collection_name)
    source_collection_iterable = source_collection.find()
    destination_collection = destination_db.get_collection(collection_name)
    for source_document in source_collection_iterable:
        conflict = identify_metadata_conflict(destination_collection, source_document)
        if conflict:
            print(
                "Conflict Found! "
                + "source_id="
                + str(conflict.source_id)
                + " destination_id="
                + str(conflict.destination_id)
            )

            merge_history_document(conflict.source_id, conflict.destination_id, destination_db)
        else:
            migrate_document(destination_collection, source_document)


def migrate_values_collection(source_db, destination_db):
    """TODO: Complete documentation.

    :param source_db:
    :param destination_db:
    :return:
    """
    collection_name = "values"
    collection_iterable = source_db.get_collection(collection_name).find()
    destination_collection = destination_db.get_collection(collection_name)
    for document in collection_iterable:
        migrate_document(destination_collection, document)


def check_merge_history_readiness(destination_db):
    """TODO: Complete documentation.

    :param destination_db:
    :return:
    """
    # look for fields that should be set when Org modeling is present. If they are missing exit.
    collection_name = "metadata"
    destination_collection = destination_db.get_collection(collection_name)
    if destination_collection.find({"workspace": {"$exists": False}}).count() > 0:
        print(
            "Database is not ready for migration. Update the connection string in "
            "C:\\ProgramData\\National Instruments\\Skyline\\Config\\TagHistorian.json to "
            "point to the nitaghistorian database in your MongoDB instance and restart Service "
            "Manager. Please see <TODO: DLINK HERE> for more detail"
        )
        sys.exit()


def migrate_within_instance(service, action, config):
    """TODO: Complete documentation.

    :param service:
    :return:
    """
    codec = bson.codec_options.CodecOptions(uuid_representation=bson.binary.UUID_SUBTYPE)
    config = get_service_config(constants.no_sql)
    client = MongoClient(
        host=[config[constants.no_sql.name]["Mongo.Host"]],
        port=config[constants.no_sql.name]["Mongo.Port"],
        username=config[constants.no_sql.name]["Mongo.User"],
        password=config[constants.no_sql.name]["Mongo.Password"],
    )
    source_db = client.get_database(name=service.SOURCE_DB, codec_options=codec)
    destination_db = client.get_database(name=service.destination_db, codec_options=codec)
    check_merge_history_readiness(destination_db)
    migrate_values_collection(source_db, destination_db)
    migrate_metadata_collection(source_db, destination_db)

