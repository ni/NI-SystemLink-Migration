import base64
import json
from manual_test.manual_test_base import ManualTestBase
from pathlib import Path
from typing import Any, Dict, Optional

GET_ALL_FILES_ROUTE = '/nifile/v1/service-groups/Default/files'
GET_FILE_ROUTE_FORMAT = '/nifile/v1/service-groups/Default/files/?id={file_id}'
UPLOAD_ROUTE = '/nifile/v1/service-groups/Default/upload-files'

ASSETS_PATH = Path(__file__).parent.parent / 'assets'
IMAGE_PATH = str(ASSETS_PATH / 'Image.png')
TDMS_PATH = str(ASSETS_PATH / 'Data.tdms')


class FileUtilities:
    def upload_inline_text_file(
        self,
        test: ManualTestBase,
        workspace: str,
        contents: str,
        filename: str,
        properties: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Uploads a string to the SystemLink server as a text file

        :param test: test instance
        :param workspace: id of the workspace to create the file in
        :param contents: text contents of the file
        :param filename: filename to use on the server
        :param properties: properties to add to the file on the server
        """
        return self.__upload_file(test, workspace, contents, filename, properties)

    def upload_file(
        self,
        test: ManualTestBase,
        workspace: str,
        path: str,
        filename: Optional[str] = None,
        properties: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Uploads a file to the SystemLink server

        :param test: test instance
        :param workspace: id of the workspace to create the file in
        :param path: local path of the file to upload
        :param filename: optional filename to use on the server, if it should be different than the local file name
        :param properties: properties to add to the file on the server
        """

        with open(path, 'rb') as contents:
            return self.__upload_file(
                test,
                workspace,
                contents,
                filename or Path(path).name,
                properties)

    def __upload_file(
        self,
        test: ManualTestBase,
        workspace: str,
        contents: Any,
        filename: str,
        properties: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        upload: Dict[str, Any] = {'file': (filename, contents)}
        if properties:
            upload['metadata'] = json.dumps(properties)

        response = test.post(
            UPLOAD_ROUTE,
            params={'workspace': workspace},
            files=upload,
            retries=test.build_default_400_retry())
        response.raise_for_status()
        return response.json()

    def get_file(self,  test: ManualTestBase, file_id: str) -> Dict[str, Any]:
        uri = GET_FILE_ROUTE_FORMAT.format(file_id=file_id)
        response = test.get(uri)
        response.raise_for_status()

        file = response.json()['availableFiles'][0]
        return self.__extract_single_file_details(test, file)

    def get_files(self, test: ManualTestBase) -> Dict[str, Dict[str, Any]]:
        take = 100
        skip = 0
        count = take
        all_files = {}
        while count == take:
            response = test.get(GET_ALL_FILES_ROUTE, params={'take': take, 'skip': skip})
            response.raise_for_status()

            received_files = response.json()['availableFiles']
            count = len(received_files)
            details = self.__extract_file_details(test, received_files)
            all_files.update(details)

            skip += take

        return all_files

    def __extract_file_details(self, test: ManualTestBase, files) -> Dict[str, Dict[str, Any]]:
        return {file['id']: file for file in [self.__extract_single_file_details(test, file) for file in files]}

    def __extract_single_file_details(self, test: ManualTestBase, file) -> Dict[str, Any]:
        data_url = file['_links']['data']['href']
        contents = self.__download_file_contents(test, data_url)
        file['contents'] = contents
        return file

    def __download_file_contents(self, test: ManualTestBase, url):
        response = test.get(url)
        response.raise_for_status()

        return base64.b64encode(response.content).decode('utf-8')
