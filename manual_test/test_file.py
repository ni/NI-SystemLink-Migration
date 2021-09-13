import json

from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from manual_test.manual_test_base import POPULATED_SERVER_RECORD_TYPE, ManualTestBase, handle_command_line
from typing import Any, Dict, List


upload_route = '/nifile/v1/service-groups/Default/upload-files'
get_route = '/nifile/v1/service-groups/Default/files'

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
        file_data = self.__get_files_to_create(workspaces)
        for data in file_data:
            file = {
                    'file': (data['filename'], data['contents']),
                    'metadata': json.dumps(data['properties'])
                   }
            workspace = data['workspace']
            response = self.post(upload_route, params={'workspace': workspace}, files=file)
            response.raise_for_status()

    def __get_files(self):
        take = 100
        skip = 0
        count = take
        all_files = []
        while count == take:
            response = self.get(get_route, params={'take': take, 'skip': skip})
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

        return response.text

    @staticmethod
    def __sorted_by_id(files):
        return sorted(files, key=lambda i: i['id'])

    @staticmethod
    def __assert_files_match(actual_files, expected_files):
        assert len(actual_files) == len(expected_files)
        assert TestFile.__sorted_by_id(actual_files) == TestFile.__sorted_by_id(expected_files)

    @staticmethod
    def __get_files_to_create(workspaces) -> List[Dict[str, Any]]:
        files: List[Dict[str, Any]] = []
        for i in range(len(workspaces)):
            for j in range(10):
                count = i * 10 + j
                files.append({
                    'filename': f'File {count}.txt',
                    'contents': f'Contents {count}',
                    'properties': {
                        f'key{count}': f'value{count}'
                    },
                    'workspace': workspaces[i]
                })

        return files

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
