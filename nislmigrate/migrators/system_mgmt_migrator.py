from nislmigrate.facades.file_system_facade import FileSystemFacade
from nislmigrate.facades.facade_factory import FacadeFactory
from nislmigrate.facades.mongo_configuration import MongoConfiguration
from nislmigrate.facades.mongo_facade import MongoFacade
from nislmigrate.extensibility.migrator_plugin import MigratorPlugin, ArgumentManager
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from nislmigrate.logs.migration_error import MigrationError
import os
import base64
import shutil
from typing import Any, Dict


SALT_FOLDER_NAME = 'salt'
SALT_FOLDER_DIRECTORY = os.path.join('National Instruments')

PKI_RELATIVE_PATH = os.path.join(
    SALT_FOLDER_DIRECTORY,
    SALT_FOLDER_NAME,
    'conf',
    'pki',
    'master')

PKI_INSTALLED_PATH = os.path.join(
    str(os.environ.get('ProgramData')),
    PKI_RELATIVE_PATH)

PILLAR_RELATIVE_PATH = os.path.join(
    SALT_FOLDER_DIRECTORY,
    SALT_FOLDER_NAME,
    'srv',
    'pillar')

PILLAR_INSTALLED_PATH = os.path.join(
    str(os.environ.get('ProgramData')),
    PILLAR_RELATIVE_PATH)

PASSWORD_ARGUMENT = 'password'

PASSWORD_ARGUMENT_HELP = 'When used with --systems or --all, encrpyts system secrets using the password specified \
after the flag, otherwise ignored. You will need to provide the same password when restoring system data.'

NO_PASSWORD_ERROR = """

Migrating systems requires a password to encrypt secrets.
The same password needs to be provided during both capture and restore by
including the following command line argument:

--systems-password <PASSWORD> 

"""

class SystemsManagementMigrator(MigratorPlugin):

    __file_facade: FileSystemFacade

    @property
    def argument(self):
        return 'systems'

    @property
    def name(self):
        return 'SystemsManagement'

    @property
    def help(self):
        return 'Migrate registered systems'

    def capture(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        self.__capture_mongo_data(facade_factory, migration_directory)
        self.__capture_file_data(arguments, facade_factory, migration_directory)

    def restore(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        self.__restore_mongo_data(facade_factory, migration_directory)
        self.__restore_file_data(arguments, facade_factory, migration_directory)

    def pre_restore_check(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_facade.validate_can_restore_database_from_directory(migration_directory, self.name)
        self.__verify_captured_salt_files_exist(facade_factory, migration_directory)
        self.__verify_password_provided(arguments)

    def pre_capture_check(self, migration_directory: str, facade_factory: FacadeFactory, arguments: Dict[str, Any]):
        self.__file_facade = facade_factory.get_file_system_facade()
        self.__verify_password_provided(arguments)

    def add_additional_arguments(self, argument_manager: ArgumentManager):
        argument_manager.add_argument(PASSWORD_ARGUMENT, help=PASSWORD_ARGUMENT_HELP, metavar='<PASSWORD>')

    def __verify_password_provided(self, arguments):
        self.__get_encrypter(arguments)

    def __capture_file_data(self, arguments, facade_factory, migration_directory):
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        pki_files_migration_directory = self.__get_pki_files_migration_directory(migration_directory)
        pillar_files_migration_directory = self.__get_pillar_files_migration_directory(migration_directory)
        file_facade.copy_directory(PKI_INSTALLED_PATH, pki_files_migration_directory, True)
        file_facade.copy_directory_if_exists(PILLAR_INSTALLED_PATH, pillar_files_migration_directory, True)
        self.__encrypt_migrated_pki_files(arguments, migration_directory)

    def __capture_mongo_data(self, facade_factory, migration_directory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.capture_database_to_directory(mongo_configuration, migration_directory, self.name)

    def __restore_file_data(self, arguments, facade_factory, migration_directory):
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        pki_files_migration_directory = self.__get_pki_files_migration_directory(migration_directory)
        pillar_files_migration_directory = self.__get_pillar_files_migration_directory(migration_directory)
        self.__decrypt_migrated_pki_files(arguments, migration_directory)
        file_facade.copy_directory(pki_files_migration_directory, PKI_INSTALLED_PATH, True)
        file_facade.copy_directory_if_exists(pillar_files_migration_directory, PILLAR_INSTALLED_PATH, True)
        self.__encrypt_migrated_pki_files(arguments, migration_directory)

    def __restore_mongo_data(self, facade_factory, migration_directory):
        mongo_facade: MongoFacade = facade_factory.get_mongo_facade()
        mongo_configuration: MongoConfiguration = MongoConfiguration(self.config(facade_factory))
        mongo_facade.restore_database_from_directory(mongo_configuration, migration_directory, self.name)

    def __encrypt_migrated_pki_files(self, arguments, migration_directory):
        path_to_encrypt = os.path.join(migration_directory, SALT_FOLDER_DIRECTORY, SALT_FOLDER_NAME)
        shutil.make_archive(path_to_encrypt, 'zip', path_to_encrypt)
        self.__file_facade.remove_directory(path_to_encrypt)
        encrypter = self.__get_encrypter(arguments)
        self.__encrypt_zip(encrypter, path_to_encrypt)

    def __decrypt_migrated_pki_files(self, arguments, migration_directory):
        path_to_decrypt = os.path.join(migration_directory, SALT_FOLDER_DIRECTORY, SALT_FOLDER_NAME)
        encrypter = self.__get_encrypter(arguments)
        self.__decrypt_zip(encrypter, path_to_decrypt)
        shutil.unpack_archive(path_to_decrypt + '.zip', path_to_decrypt, 'zip')
        self.__file_facade.remove_directory(path_to_decrypt + '.zip')

    def __encrypt_zip(self, encrypter: Fernet, path: str):
        with open(path + '.zip', 'rb') as file:
            text = file.read()
        encrypted_text = encrypter.encrypt(text)
        with open(path, 'wb') as file:
            file.write(encrypted_text)
        os.remove(path + '.zip')

    def __decrypt_zip(self, encrypter: Fernet, path: str):
        with open(path, 'rb') as file:
            encrypted_text = file.read()
        text = encrypter.decrypt(encrypted_text)
        with open(path + '.zip', 'wb') as file:
            file.write(text)
        os.remove(path)

    def __verify_captured_salt_files_exist(self, facade_factory, migration_directory):
        file_facade: FileSystemFacade = facade_factory.get_file_system_facade()
        migrated_salt_directory = os.path.join(migration_directory, SALT_FOLDER_DIRECTORY, SALT_FOLDER_NAME)
        if not file_facade.does_file_exist(migrated_salt_directory):
            raise FileNotFoundError(f"Could not find the captured service at '{migrated_salt_directory}'")

    @staticmethod
    def __get_encrypter(arguments):
        password: str = arguments.get(PASSWORD_ARGUMENT, "")
        password = bytes(password, 'utf-8')
        if not password:
            raise MigrationError(NO_PASSWORD_ERROR)
        key_derivation_function = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, iterations=320000, salt=b'0'*16)
        key = base64.urlsafe_b64encode(key_derivation_function.derive(password))
        return Fernet(key)

    @staticmethod
    def __get_pki_files_migration_directory(migration_directory: str) -> str:
        return os.path.join(migration_directory, PKI_RELATIVE_PATH)

    @staticmethod
    def __get_pillar_files_migration_directory(migration_directory: str) -> str:
        return os.path.join(migration_directory, PILLAR_RELATIVE_PATH)
