import json
from manual_test_base import ManualTestBase, handle_command_line


upload_route = '/nifile/v1/service-groups/Default/upload-files'
get_route = '/nifile/v1/service-groups/Default/files'
auth_route = '/niauth/v1/auth'


class TestFile(ManualTestBase):
    def populate_data(self):
        self.__raise_if_existing_data()
        workspaces = self.__get_workspaces()
        self.__upload_files(workspaces)

    def capture_initial_data(self):
        """The file service should not be populated with initial data."""
        pass

    def validate_data(self):
        workspaces = self.__get_workspaces()
        expected_files = self.__get_expected_files(workspaces)
        data = self.__get_files(len(expected_files))
        self.__assert_file_count(data, len(expected_files))

        actual_files = self.__extract_file_details(data)
        self.__assert_files_match(actual_files, expected_files)

    def __raise_if_existing_data(self):
        response = self.get(get_route, params={'take': 1})
        if response.status_code == 404:
            return

        response.raise_for_status()
        data = response.json()
        if data['availableFiles']:
            raise RuntimeError('There is exising file data on the server')

    def __upload_files(self, workspaces):
        file_data = self.__get_expected_files(workspaces)
        for filename, data in file_data.items():
            file = {
                    'file': (filename, data['contents']),
                    'metadata': json.dumps(data['properties'])
                   }
            workspace = data['workspace']
            response = self.post(upload_route, params={'workspace': workspace}, files=file)
            response.raise_for_status()

    def __get_files(self, expected_count):
        response = self.get(get_route, params={'take': expected_count})
        response.raise_for_status()

        return response.json()

    def __get_workspaces(self):
        response = self.get(auth_route)
        response.raise_for_status()

        auth = response.json()
        workspaces = [workspace['id'] for workspace in auth['workspaces'] if workspace['enabled']]
        if len(workspaces) < 2:
            raise RuntimeError('User needs access to at least 2 workspaces')

        return workspaces

    def __extract_file_details(self, data):
        availableFiles = data['availableFiles']
        return {filename: file_data
                for filename, file_data
                in [self.__extract_single_file_details(availableFile)
                    for availableFile in availableFiles]}

    def __extract_single_file_details(self, availableFile):
        dataUrl = availableFile['_links']['data']['href']
        contents = self.__download_file_contents(dataUrl)
        filename = availableFile['properties']['Name']
        properties = {k: v for k, v in availableFile['properties'].items() if k != 'Name'}
        workspace = availableFile['workspace']
        return (filename, {'contents': contents, 'properties': properties, 'workspace': workspace})

    def __download_file_contents(self, url):
        response = self.get(url)
        response.raise_for_status()

        return response.text

    def __assert_file_count(self, data, expected_count):
        totalFiles = data['totalCount']
        actualFiles = data['availableFiles']

        assert totalFiles == expected_count
        assert len(actualFiles) == expected_count

    def __assert_files_match(self, actual_files, expected_files):
        assert actual_files == expected_files

    def __get_expected_files(self, workspaces):
        files = {}
        for i in range(len(workspaces)):
            for j in range(10):
                count = i * 10 + j
                files[f'File {count}.txt'] = {
                    'contents': f'Contents {count}',
                    'properties': {
                        f'key{count}': f'value{count}'
                    },
                    'workspace': workspaces[i]
                }

        return files


if __name__ == '__main__':
    handle_command_line(TestFile)
