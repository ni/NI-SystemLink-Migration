import json
from manual_test.manual_test_base import ManualTestBase
from pathlib import Path
from typing import Any, Dict, Optional

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
