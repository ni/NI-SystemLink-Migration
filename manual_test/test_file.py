import base64
import json

from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from manual_test.manual_test_base import POPULATED_SERVER_RECORD_TYPE, ManualTestBase, handle_command_line
from pathlib import Path
from typing import Any, Dict, List


UPLOAD_ROUTE = '/nifile/v1/service-groups/Default/upload-files'
GET_ROUTE = '/nifile/v1/service-groups/Default/files'

ASSETS_PATH = Path(__file__).parent / 'assets'
IMAGE_PATH = ASSETS_PATH / 'Image.png'

SERVICE_NAME = 'Files'
COLLECTION_NAME = 'FileIngestion'


class TestFile(ManualTestBase):

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
            upload: Dict[str, Any] = {
                    'metadata': json.dumps(file_spec['properties'])
                   }
            workspace = file_spec['workspace']

            if file_spec.get('inlineTextContents', None):
                upload['file'] = (file_spec['filename'], file_spec['inlineTextContents'])
                self.__upload_file(upload, workspace)
            else:
                with open(file_spec['contentsFile'], 'rb') as contents:
                    upload['file'] = (file_spec['filename'], contents)
                    self.__upload_file(upload, workspace)

    def __upload_file(self, upload, workspace):
        response = self.post(
            UPLOAD_ROUTE,
            params={'workspace': workspace},
            files=upload,
            retries=self.build_default_400_retry())
        response.raise_for_status()

    def __get_files(self):
        take = 100
        skip = 0
        count = take
        all_files = []
        while count == take:
            response = self.get(GET_ROUTE, params={'take': take, 'skip': skip})
            response.raise_for_status()

            received_files = response.json()['availableFiles']
            count = len(received_files)
            details = self.__extract_file_details(received_files)
            all_files.extend(details)

            skip += take

        return all_files

    def __extract_file_details(self, files) -> List[Dict[str, Any]]:
        return [self.__extract_single_file_details(file)
                for file in files]

    def __extract_single_file_details(self, file) -> Dict[str, Any]:
        data_url = file['_links']['data']['href']
        contents = self.__download_file_contents(data_url)
        file['contents'] = contents
        return file

    def __download_file_contents(self, url):
        response = self.get(url)
        response.raise_for_status()

        return base64.b64encode(response.content).decode('utf-8')

    @staticmethod
    def __sorted_by_id(files):
        return sorted(files, key=lambda i: i['id'])

    @staticmethod
    def __assert_files_match(actual_files, expected_files):
        assert len(actual_files) == len(expected_files)
        assert TestFile.__sorted_by_id(actual_files) == TestFile.__sorted_by_id(expected_files)

    @staticmethod
    def __get_files_to_create(workspaces) -> List[Dict[str, Any]]:
        files_specs: List[Dict[str, Any]] = []
        for i in range(len(workspaces)):
            files_specs.append(TestFile.__create_text_file(i, workspaces[i]))
            files_specs.append(TestFile.__create_png_file(i, workspaces[i]))

        return files_specs

    @staticmethod
    def __create_text_file(index: int, workspace: str) -> Dict[str, Any]:
        return {
                'filename': f'File {index}.txt',
                'inlineTextContents': f'Contents {index}',
                'properties': {
                    f'key{index}': f'value{index}'
                },
                'workspace': workspace
            }

    @staticmethod
    def __create_png_file(index: int, workspace: str) -> Dict[str, Any]:
        return {
                'filename': 'Image.png',
                'contentsFile': IMAGE_PATH,
                'properties': {
                    f'image{index}': f'imageValue{index}'
                },
                'workspace': workspace
            }

    def __record_data(self, record_type: str):
        self.record_data(
            SERVICE_NAME,
            COLLECTION_NAME,
            record_type,
            self.__get_files())

    def __read_recorded_data(self, record_type: str):
        return self.read_recorded_data(
            SERVICE_NAME,
            COLLECTION_NAME,
            record_type)


if __name__ == '__main__':
    handle_command_line(TestFile)
