from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin

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


class THDBBugMigrator(MigratorPlugin):

    @property
    def argument(self):
        return "thdbbug"

    @property
    def name(self):
        return "THDBBugFixer"

    @property
    def help(self):
        return "Migrate tag history data to the correct MongoDB to resolve an issue introduced" \
               " in SystemLink 2020R2 when using a remote Mongo instance."

    def capture(self, migration_directory: str, facade_factory: FacadeFactory):
        pass

    def restore(self, migration_directory: str, facade_factory: FacadeFactory):
        pass

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory) -> None:
        pass

    def migrate_within_instance(service, action, config):
        if not action == constants.thdbbug.arg:
            return
        codec = bson.codec_options.CodecOptions(uuid_representation=bson.binary.UUID_SUBTYPE)
        no_sql_config = get_service_config(constants.no_sql)
        client = MongoClient(host=[no_sql_config[constants.no_sql.name]['Mongo.Host']],
                             port=no_sql_config[constants.no_sql.name]['Mongo.Port'],
                             username=no_sql_config[constants.no_sql.name]['Mongo.User'],
                             password=no_sql_config[constants.no_sql.name]['Mongo.Password'])
        source_db = client.get_database(name=service.source_db, codec_options=codec)
        destination_db = client.get_database(name=service.destination_db, codec_options=codec)
        check_merge_history_readiness(destination_db)
        migrate_values_collection(source_db, destination_db)
        migrate_metadata_collection(source_db, destination_db)

    def migrate_metadata_collection(source_db, destination_db):
        collection_name = 'metadata'
        source_collection = source_db.get_collection(collection_name)
        source_collection_iterable = source_collection.find()
        destination_collection = destination_db.get_collection(collection_name)
        for source_document in source_collection_iterable:
            conflict = identify_metadata_conflict(destination_collection, source_document)
            if conflict:
                print("Conflict Found! " + "source_id=" + str(conflict.source_id) + " destination_id=" + str(
                    conflict.destination_id))
                merge_history_document(conflict.source_id, conflict.destination_id, destination_db)
            else:
                migrate_document(destination_collection, source_document)

    def migrate_values_collection(source_db, destination_db):
        collection_name = 'values'
        collection_iterable = source_db.get_collection(collection_name).find()
        destination_collection = destination_db.get_collection(collection_name)
        for document in collection_iterable:
            migrate_document(destination_collection, document)
