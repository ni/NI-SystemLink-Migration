import base64

from manual_test.utilities.file_utilities import FileUtilities
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from manual_test.manual_test_base import POPULATED_SERVER_RECORD_TYPE, ManualTestBase, handle_command_line
from pathlib import Path
from typing import Any, Dict, List


GET_ROUTE = '/nifile/v1/service-groups/Default/files'

ASSETS_PATH = Path(__file__).parent / 'assets'
IMAGE_PATH = ASSETS_PATH / 'Image.png'
TDMS_PATH = ASSETS_PATH / 'Data.tdms'

SERVICE_NAME = 'Files'
COLLECTION_NAME = 'FileIngestion'


class TestFile(ManualTestBase):

    __file_utilities = FileUtilities()

    def populate_data(self):
        WorkspaceUtilities().create_workspace('WorkspaceForManualFilesMigrationTest', self)
        workspaces = WorkspaceUtilities().get_workspaces(self)
        self.__upload_files(workspaces)
        self.__record_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self):
        """The file service should not be populated with initial data."""
        pass

    def validate_data(self):
        expected_files = self.__read_recorded_data(POPULATED_SERVER_RECORD_TYPE)
        actual_files = self.__get_files()

        self.__assert_files_match(actual_files, expected_files)

    def __upload_files(self, workspaces):
        file_specs = self.__get_files_to_create(workspaces)
        for file_spec in file_specs:
            workspace = file_spec['workspace']
            properties = file_spec['properties']
            inline_text_contents = file_spec.get('inlineTextContents', None)
            filename = file_spec['filename']

            if inline_text_contents:
                self.__file_utilities.upload_inline_text_file(
                    self,
                    workspace,
                    inline_text_contents,
                    filename,
                    properties)
            else:
                path = file_spec['contentsFile']
                self.__file_utilities.upload_file(
                    self,
                    workspace,
                    path,
                    filename,
                    properties)

    def __get_files(self) -> Dict[str, Dict[str, Any]]:
        take = 100
        skip = 0
        count = take
        all_files = {}
        while count == take:
            response = self.get(GET_ROUTE, params={'take': take, 'skip': skip})
            response.raise_for_status()

            received_files = response.json()['availableFiles']
            count = len(received_files)
            details = self.__extract_file_details(received_files)
            all_files.update(details)

            skip += take

        return all_files

    def __extract_file_details(self, files) -> Dict[str, Dict[str, Any]]:
        return {file['id']: file for file in [self.__extract_single_file_details(file) for file in files]}

    def __extract_single_file_details(self, file) -> Dict[str, Any]:
        data_url = file['_links']['data']['href']
        contents = self.__download_file_contents(data_url)
        file['contents'] = contents
        return file

    def __download_file_contents(self, url):
        response = self.get(url)
        response.raise_for_status()

        return base64.b64encode(response.content).decode('utf-8')

    def __assert_files_match(self, actual_files, expected_files):
        if self._relax_validation:
            self.__assert_files_relaxed_match(actual_files, expected_files)
        else:
            self.__assert_files_strict_match(actual_files, expected_files)

    @staticmethod
    def __assert_files_strict_match(actual_files, expected_files):
        assert actual_files == expected_files

    @staticmethod
    def __assert_files_relaxed_match(actual_files, expected_files):
        assert len(actual_files) >= len(expected_files)
        for id, file in expected_files.items():
            assert actual_files[id] == file

    @staticmethod
    def __get_files_to_create(workspaces) -> List[Dict[str, Any]]:
        files_specs: List[Dict[str, Any]] = []
        for i in range(len(workspaces)):
            files_specs.append(TestFile.__create_text_file_spec(i, workspaces[i]))
            files_specs.append(TestFile.__create_png_file_spec(i, workspaces[i]))
            files_specs.append(TestFile.__create_tdms_file_spec(i, workspaces[i]))

        return files_specs

    @staticmethod
    def __create_text_file_spec(index: int, workspace: str) -> Dict[str, Any]:
        return {
                'filename': f'File {index}.txt',
                'inlineTextContents': f'Contents {index}',
                'properties': {
                    f'key{index}': f'value{index}'
                },
                'workspace': workspace
            }

    @staticmethod
    def __create_png_file_spec(index: int, workspace: str) -> Dict[str, Any]:
        return {
                'filename': IMAGE_PATH.name,
                'contentsFile': IMAGE_PATH,
                'properties': {
                    f'image{index}': f'imageValue{index}'
                },
                'workspace': workspace
            }

    @staticmethod
    def __create_tdms_file_spec(index: int, workspace: str) -> Dict[str, Any]:
        return {
                'filename': TDMS_PATH.name,
                'contentsFile': TDMS_PATH,
                'properties': {
                    f'tdms{index}': f'tdmsValue{index}'
                },
                'workspace': workspace
            }

    def __record_data(self, record_type: str):
        self.record_data(
            SERVICE_NAME,
            COLLECTION_NAME,
            record_type,
            [self.__get_files()])

    def __read_recorded_data(self, record_type: str):
        files = self.read_recorded_data(
            SERVICE_NAME,
            COLLECTION_NAME,
            record_type)
        return files[0]


if __name__ == '__main__':
    handle_command_line(TestFile)
