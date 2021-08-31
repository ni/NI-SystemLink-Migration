import json
from manual_test_base import ManualTestBase

file_data = {
        f'File {i}.txt': {
            'contents': f'Contents {i}',
            'properties': {
                f'key{i}': f'value{i}'
            }
        } for i in range(1, 100)
    }

upload_route = '/nifile/v1/service-groups/Default/upload-files'
get_route = '/nifile/v1/service-groups/Default/files'


class TestFile(ManualTestBase):
    def populate_data(self):
        self.__raise_if_existing_data()
        self.__upload_files()

    def validate_data(self):
        data = self.__get_files()
        self.__assert_file_count(data)

        actual_files = self.__extract_file_details(data)
        self.__assert_files_match(actual_files)

    def __raise_if_existing_data(self):
        response = self.get(get_route, params={'take': 1})
        if response.status_code == 404:
            return

        response.raise_for_status()
        data = response.json()
        if data['availableFiles']:
            raise Exception('There is existing file data on the server')

    def __upload_files(self):
        for filename, data in file_data.items():
            file = {
                    'file': (filename, data['contents']),
                    'metadata': json.dumps(data['properties'])
                   }
            response = self.post(upload_route, files=file)
            response.raise_for_status()

    def __get_files(self):
        response = self.get(get_route, params={'take': len(file_data)})
        response.raise_for_status()

        return response.json()

    def __extract_file_details(self, data):
        availableFiles = data['availableFiles']
        return {filename: properties
                for filename, properties
                in [self.__extract_single_file_details(availableFile)
                    for availableFile in availableFiles]}

    def __extract_single_file_details(self, availableFile):
        dataUrl = availableFile['_links']['data']['href']
        contents = self.__download_file_contents(dataUrl)
        filename = availableFile['properties']['Name']
        properties = {k: v for k, v in availableFile['properties'].items() if k != 'Name'}
        return (filename, {'contents': contents, 'properties': properties})

    def __download_file_contents(self, url):
        response = self.get(url)
        response.raise_for_status()

        return response.text

    def __assert_file_count(self, data):
        totalFiles = data['totalCount']
        actualFiles = data['availableFiles']

        expectedCount = len(file_data)

        if totalFiles != expectedCount:
            raise Exception(f'Expected {expectedCount} files but total on server i {totalFiles}')
        if len(actualFiles) != expectedCount:
            raise Exception(f'Expected {expectedCount} files but response contained {len(actualFiles)}')

    def __assert_files_match(self, actual_files):
        if actual_files != file_data:
            raise Exception('They did not match')


if __name__ == '__main__':
    ManualTestBase.handle_command_line(TestFile)
