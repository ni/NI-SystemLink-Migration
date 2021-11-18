"""Handle file and directory operations."""

import json
import os
import shutil
import stat
import base64

from nislmigrate.logs.migration_error import MigrationError
from nislmigrate.migration_action import MigrationAction
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

COMPRESSION_FORMAT = 'tar'


class FileSystemFacade:
    """
    Handles operations that act on the real file system.
    """
    def determine_migration_directory_for_service(self,
                                                  migration_directory_root: str,
                                                  service_name: str) -> str:
        """
        Generates the migration directory for a particular service.

        :param service_name: The name of the service to determine the migration directory for.
        :return: The migration directory for the service.
        """
        return os.path.join(migration_directory_root, service_name)

    def does_directory_exist(self, directory: str) -> bool:
        """
        Determines whether a directory exists.

        :param dir_: The directory path to check.
        :return: True if the given directory path is a directory and exists.
        """
        return os.path.isdir(directory)

    def does_file_exist_in_directory(self,
                                     directory: str,
                                     file_name: str) -> bool:
        """
        Determines whether a file with the given name exists in a directory

        :param directory: The directory to check.
        :param file_name: The file to check.
        :return: True if the file exists in the given directory.
        """
        path = os.path.join(directory, file_name)
        return self.does_file_exist(path)

    def does_file_exist(self, file_path: str) -> bool:
        """
        Determines whether a file exists on disk.

        :param file_path: The path to check.
        :return: True if the file exists.
        """
        return os.path.isfile(file_path)

    def remove_directory(self, directory: str):
        """
        Deletes the given directory and its children.

        :param dir_: The directory to remove.
        :return: None.
        """
        if os.path.isdir(directory):
            shutil.rmtree(directory, onerror=self.__on_error_remove_readonly_and_retry)

    def migrate_singlefile(self,
                           migration_directory_root: str,
                           service_name: str,
                           single_file_source_directory: str,
                           single_file_name: str,
                           action: MigrationAction):
        """
        Perform a capture or restore the given service.

        :param migration_directory_root: The root directory migration is taking place from.
        :param action: Whether to capture or restore.
        :return: None.
        """
        root = migration_directory_root
        migration_dir = self.determine_migration_directory_for_service(root, service_name)
        if action == MigrationAction.CAPTURE:
            self.remove_directory(migration_dir)
            os.mkdir(migration_dir)
            singlefile_full_path = os.path.join(
                single_file_source_directory,
                single_file_name,
            )
            shutil.copy(singlefile_full_path, migration_dir)
        elif action == MigrationAction.RESTORE:
            singlefile_full_path = os.path.join(migration_dir, single_file_name)
            shutil.copy(singlefile_full_path, single_file_source_directory)

    def capture_single_file(self,
                            migration_directory_root: str,
                            service_name: str,
                            restore_directory: str,
                            file: str):
        root = migration_directory_root
        migration_dir = self.determine_migration_directory_for_service(root, service_name)
        self.remove_directory(migration_dir)
        os.mkdir(migration_dir)
        singlefile_full_path = os.path.join(
            restore_directory,
            file,
        )
        shutil.copy(singlefile_full_path, migration_dir)

    def restore_single_file(self,
                            migration_directory_root: str,
                            service_name: str,
                            restore_directory: str,
                            file: str):
        root = migration_directory_root
        migration_dir = self.determine_migration_directory_for_service(root, service_name)
        singlefile_full_path = os.path.join(migration_dir, file)
        shutil.copy(singlefile_full_path, restore_directory)

    def read_json_file(self, path: str) -> dict:
        """
        Reads json from a file.

        :param path: The path to the json file to read.
        :return: The parsed json from the file.
        """
        with open(path, encoding='utf-8-sig') as json_file:
            return json.load(json_file)

    @staticmethod
    def copy_file(from_directory: str, to_directory: str, file_name: str):
        """
        Copy an entire directory from one location to another.

        :param from_directory: The directory the file to copy exists in.
        :param to_directory: The directory to copy the file into.
        :param file_name: The name of the file to copy.
        """
        if not os.path.exists(to_directory):
            os.mkdir(to_directory)
        file_path = os.path.join(from_directory, file_name)
        shutil.copy(file_path, to_directory)

    def copy_directory(self, from_directory: str, to_directory: str, force: bool):
        """
        Copy an entire directory from one location to another.

        :param from_directory: The directory whose contents to copy.
        :param to_directory: The directory to put the copied contents.
        :param force: Whether to delete existing content in to_directory before copying.
        """
        if os.path.exists(to_directory) and os.listdir(to_directory) and not force:
            error = "The tool can not copy to the non empty directory: '%s'" % to_directory
            raise MigrationError(error)
        if not os.path.exists(from_directory):
            raise MigrationError("No data found at: '%s'" % from_directory)

        self.remove_directory(to_directory)
        shutil.copytree(from_directory, to_directory)

    def copy_directory_to_encrypted_file(self, from_directory: str, encrypted_file_path: str, secret: str):
        """
        Copy an entire directory from one location to another and encrypts it.

        :param from_directory: The directory whose contents to copy.
        :param encrypted_file_path: The directory to put the copied contents.
        :param secret: A password to use when encrypting the directory.
        """

        if self.does_file_exist(encrypted_file_path):
            raise FileExistsError("Captured data already exists: '%s'" % encrypted_file_path)
        if not self.does_directory_exist(from_directory):
            raise FileExistsError("No data found at: '%s'" % from_directory)
        extension = f'.{COMPRESSION_FORMAT}'
        if self.does_file_exist(from_directory + extension):
            raise FileExistsError(f'Data not cleaned up from previous migration: {from_directory + extension}')

        # shutil.make_archive automatically appends the compression formats file extension to the output path.
        shutil.make_archive(from_directory, COMPRESSION_FORMAT, from_directory)
        self.__encrypt_tar(secret, from_directory + extension, encrypted_file_path)
        os.remove(from_directory + extension)

    def copy_directory_from_encrypted_file(self, encrypted_file_path: str, to_directory: str, secret: str):
        """
        Copy an entire directory from one location to another and encrypts it.

        :param encrypted_file_path: The directory whose contents to copy.
        :param to_directory: The directory to put the copied contents.
        :param secret: A password to use when encrypting the directory.
        """

        if not self.does_file_exist(encrypted_file_path):
            raise MigrationError("No data found at: '%s'" % encrypted_file_path)
        extension = f'.{COMPRESSION_FORMAT}'
        if self.does_file_exist(encrypted_file_path + extension):
            raise MigrationError(f'Data not cleaned up from previous migration: {encrypted_file_path + extension}')

        self.__decrypt_tar(secret, encrypted_file_path, encrypted_file_path + extension)
        shutil.unpack_archive(encrypted_file_path + extension, to_directory, COMPRESSION_FORMAT)
        os.remove(encrypted_file_path + extension)

    def write_file(self, path: str, content: str) -> None:
        """
        Writes a file to the indicated path with the given content.

        :param path: The path to the file to write.
        :param content: The contents to write in the file.
        """
        with open(path, 'w') as file:
            file.write(content)

    def read_file(self, path: str) -> str:
        """
        Reads the contents from a file at the indicated path.

        :param path: The path to the file to read.
        """
        if not self.does_file_exist(path):
            raise MigrationError(f'Unable to read file at {path} because it does not exist.')
        with open(path, 'r') as file:
            return file.read()

    def __encrypt_tar(self, secret: str, tar_path: str, encrypted_path: str):
        with open(tar_path, 'rb') as file:
            text = file.read()
        encrypter = self.__get_encrypter(secret)
        encrypted_text = encrypter.encrypt(text)
        with open(encrypted_path, 'wb') as file:
            file.write(encrypted_text)

    def __decrypt_tar(self, secret: str, encrypted_path: str, tar_path: str):
        with open(encrypted_path, 'rb') as file:
            encrypted_text = file.read()
        encrypter = self.__get_encrypter(secret)
        text = encrypter.decrypt(encrypted_text)
        with open(tar_path, 'wb') as file:
            file.write(text)

    @staticmethod
    def __get_encrypter(secret: str):
        password = bytes(secret, 'utf-8')
        if not password:
            raise MigrationError('Secret not provided via the --secret flag for encryption.')
        key_derivation_function = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, iterations=320000, salt=b'0'*16)
        key = base64.urlsafe_b64encode(key_derivation_function.derive(password))
        return Fernet(key)

    def copy_directory_if_exists(self, from_directory: str, to_directory: str, force: bool) -> bool:
        """
        Calls copy_directory only if the source directory exists. See copy_directory for parameter descriptions.

        :return True if a copy happened, otherwise false.
        """
        if os.path.exists(from_directory):
            self.copy_directory(from_directory, to_directory, force)
            return True
        else:
            return False

    def __on_error_remove_readonly_and_retry(self, func, path, execinfo):
        """
        Error handler that removes the readonly attribute from a file path
        and then retries the previous operation.

        :param func: A continuation to run with the path.
        :param path: The path to remove the readonly attribute from.
        :param execinfo: Will be the exception information returned by sys.exc_info()
        :return: None.
        """
        self.__remove_readonly(path)
        func(path)

    def __remove_readonly(self, path):
        """
        Removes the read-only attribute from a file or directory.

        :param path: The path to remove the readonly attribute from.
        """
        os.chmod(path, stat.S_IWRITE)
