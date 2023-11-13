import argparse
import json
import os
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
import requests
from typing import Any, Dict, List, Optional, Tuple, Type
from urllib.parse import urljoin
from urllib3 import disable_warnings, exceptions
from urllib3.util import Retry

# Record type for data recorded from a clean server prior to restoring data
CLEAN_SERVER_RECORD_TYPE: str = 'clean'
# Record type for data recorded from a server which is populated with test data
POPULATED_SERVER_RECORD_TYPE: str = 'populated'


class ManualTestBase:

    disable_warnings(exceptions.InsecureRequestWarning)

    def __init__(self, server: str, relax_validation: bool, username: str = None, password: str = None, sle_token: str = None) -> None:
        """
        Constructs the manual test base class.

        :param server: The url of the SystemLink Server, for example https://systemlink.example.com
        :param username: The username to use to log in to the server.
        :param password: The password to use to log in to the server.
        :param relax_validation: Relax validation for tests that cannot easily validate extra data.
        :return: None.
        """
        self._token = None
        self._auth = None

        self._server = server
        if sle_token:
            self._token = sle_token
        else:
            self._auth = HTTPBasicAuth(username, password)
        self._relax_validation = relax_validation

    def populate_data(self) -> None:
        """
        Derived class should override to populate the SystemLink server with test data.
        """

        raise NotImplementedError

    def record_initial_data(self) -> None:
        """
        Derived class should override to record the initial state of the SystemLink server prior
        to running a restore operation. Recorded data should be used by the validate_data() method.
        """

        raise NotImplementedError

    def validate_data(self) -> None:
        """
        Derived class should override to validate the SystemLink server contains the test
        data added by populate_data. validate_data and populate_data can be called from
        separate processes, so cannot depend on state to validate data.
        """

        raise NotImplementedError

    def request(self, method: str, route: str, retries: Optional[Retry] = None, **kwargs) -> requests.Response:
        """
        Sends a request.

        :param method: Method for the request. See requests.request.
        :param route: URL for the request, relative to self.server.
        :param retries: Description of how to retry if the request failes. Default is no retry.
        :param kwargs: See requests.request
        """

        with requests.Session() as session:
            if retries:
                session.mount(self._server, HTTPAdapter(max_retries=retries))

            if self._auth:
                return session.request(
                    method,
                    urljoin(self._server, route),
                    auth=kwargs.pop('auth', self._auth),
                    verify=kwargs.pop('verify', False),
                    **kwargs)
            else:
                session.headers.update({'x-ni-api-key': self._token})
                return session.request(
                    method,
                    urljoin(self._server, route),
                    verify=kwargs.pop('verify', False),
                    **kwargs)

    def get(self, route: str, retries: Optional[Retry] = None, **kwargs) -> requests.Response:
        """
        Sends a get request. See self.request for parameter details.
        """

        return self.request('GET', route, retries, **kwargs)

    def patch(self, route: str, retries: Optional[Retry] = None, **kwargs) -> requests.Response:
        """
        Sends a patch request. See self.request for parameter details.
        """

        return self.request('PATCH', route, retries, **kwargs)

    def post(self, route: str, retries: Optional[Retry] = None, **kwargs) -> requests.Response:
        """
        Sends a post request. See self.request for parameter details.
        """

        return self.request('POST', route, retries, **kwargs)

    def put(self, route: str, retries: Optional[Retry] = None, **kwargs) -> requests.Response:
        """
        Sends a put request. See self.request for parameter details.
        """

        return self.request('PUT', route, retries, **kwargs)

    def get_all_with_skip_take(self, route: str, data_key: str) -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]] = []
        skip = 0
        take = 50
        additional_data = self.__get_data_with_skip_take(route, data_key, skip, take)
        while additional_data:
            data.extend(additional_data)
            skip = skip + take
            additional_data = self.__get_data_with_skip_take(route, data_key, skip, take)

        return data

    def __get_data_with_skip_take(
        self,
        route: str,
        data_key: str,
        skip: int,
        take: int
    ) -> List[Dict[str, Any]]:
        params = {'skip': skip, 'take': take}
        response = self.get(route, params=params)
        response.raise_for_status()
        return response.json()[data_key]

    def get_all_with_continuation_token(self, route: str, data_key: str) -> List[Dict[str, Any]]:
        data, continuation_token = self.__request_data_and_continuation_token('GET', route, data_key)
        while continuation_token:
            additional_data, continuation_token = self.__request_data_and_continuation_token(
                    'GET', route, data_key, params={'continuationToken': continuation_token})
            data.extend(additional_data)

        return data

    def query_all_with_continuation_token(
        self,
        route: str,
        query: Dict[str, Any],
        data_key: str
    ) -> List[Dict[str, Any]]:
        data, continuation_token = self.__request_data_and_continuation_token(
            'POST',
            route,
            data_key,
            json=query)
        while continuation_token:
            query['continuationToken'] = continuation_token
            additional_data, continuation_token = self.__request_data_and_continuation_token(
                'POST', route, data_key, json=query)
            data.extend(additional_data)

        return data

    def __request_data_and_continuation_token(
        self,
        method: str,
        route: str,
        data_key: str,
        **kwargs
    ) -> Tuple[List[Dict[str, Any]], str]:
        response = self.request(method, route, **kwargs)
        response.raise_for_status()
        data = response.json()
        return data[data_key], data.get('continuationToken', None)

    def build_default_400_retry(self, method='POST') -> Retry:
        """
        Builds a standard Retry object for retrying 400 errors on a route.

        This is necessary due to a caching issue encountered by tests that create
        new workspaces. For a short window after the workspace is created, the auth
        token will not have refreshed and operations that reference the workspace will
        fail.
        """
        return Retry(total=5, backoff_factor=2, status_forcelist=[400], allowed_methods=method)

    def read_recorded_json_data(
            self,
            category: str,
            collection: str,
            record_type: str,
            required: bool = True
    ) -> List[Dict[str, Any]]:
        """
            Read recorded JSON data from a file.

            :param category: Unique category for this record. Corresponds to a folder on disk.
            :param collection: Unique collection name being read.
            :param record_type: Record type being read.
            :required: If true, this method will fail if the file does not exist.
            :return: The file contents, or an empty list if not required and the file does not exist.
        """
        file_path = self.__build_recording_file_path(
            category,
            collection,
            record_type,
            '.json',
            create_folder_if_missing=False)

        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception:
            if required:
                msg = f'Unable to read recording file for category="{category}"; collection="{collection}"'
                raise RuntimeError(msg)

        return []

    def read_recorded_text(
            self,
            category: str,
            collection: str,
            record_type: str,
            required: bool = True
    ) -> str:
        """
            Read recorded text data from a file.

            :param category: Unique category for this record. Corresponds to a folder on disk.
            :param collection: Unique collection name being read.
            :param record_type: Record type being read.
            :required: If true, this method will fail if the file does not exist.
            :return: The file contents, or an empty string if not required and the file does not exist.
        """
        file_path = self.__build_recording_file_path(
            category,
            collection,
            record_type,
            '.txt',
            create_folder_if_missing=False)

        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception:
            if required:
                msg = f'Unable to read recording file for category="{category}"; collection="{collection}"'
                raise RuntimeError(msg)

        return ''

    def record_json_data(self, category: str, collection: str, record_type: str, data: List[Dict[str, Any]]) -> None:
        """
            Save service data to a file as JSON for later validation.

            :param category: Unique category for this record. Corresponds to a folder on disk.
            :param collection: Unique collection name being recorded.
            :param record_type: Record type being recorded.
            :data: The data to record.
        """
        file_path = self.__build_recording_file_path(
            category,
            collection,
            record_type,
            '.json',
            create_folder_if_missing=True)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def record_text(self, category: str, collection: str, record_type: str, data: str) -> None:
        """
            Save service data to a file as raw text for later validation.

            :param category: Unique category for this record. Corresponds to a folder on disk.
            :param collection: Unique collection name being recorded.
            :param record_type: Record type being recorded.
            :data: The data to record.
        """
        file_path = self.__build_recording_file_path(
            category,
            collection,
            record_type,
            '.txt',
            create_folder_if_missing=True)
        # Fixup line endings
        data = data.replace('\r\n', '\n')
        with open(file_path, 'w') as file:
            file.write(data)

    def __build_recording_file_path(
            self,
            category: str,
            collection: str,
            record_type: str,
            extension: str,
            create_folder_if_missing: bool
    ) -> str:
        folder_path = os.path.join(os.getcwd(), '.test', category)
        if create_folder_if_missing:
            os.makedirs(folder_path, exist_ok=True)

        filename = collection + '.' + record_type + extension
        return os.path.join(folder_path, filename)

    def datetime_to_string(self, time) -> str:
        """Converts a datetime object to a string in the format expected by SystemLink"""
        return time.strftime('%Y-%m-%dT%H:%M:%SZ')

    def find_record_with_matching_id(
            self,
            source: Dict[str, Any],
            collection: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Finds a record in a collection with the same 'id' value as target."""
        return self.find_record_with_matching_property_value(source, collection, 'id')

    def find_record_with_matching_property_value(
        self,
        source: Dict[str, Any],
        collection: List[Dict[str, Any]],
        property: str,
    ) -> Optional[Dict[str, Any]]:
        """Finds a record in a collection with the same value for property as target"""
        return self.find_record_by_property_value(source[property], collection, property)

    def find_record_by_id(
            self,
            id: str,
            collection: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Finds a record in a collection which has an 'id' field matching the input."""
        return self.find_record_by_property_value(id, collection, 'id')

    @staticmethod
    def find_record_by_property_value(
            property_value: Any,
            collection: List[Dict[str, Any]],
            property: str
    ) -> Optional[Dict[str, Any]]:
        """Finds a record in a collection which has an field matching value for the given property."""
        return next((record for record in collection if record[property] == property_value), None)


def handle_command_line(test_class: Type[ManualTestBase]) -> None:
    """
    Parses command line arguments, instantiates a test class,
    and populates or verifies data.

    :param test_class: The test class to instantiate
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', required=True, help='systemlink server url. eg https://server')
    parser.add_argument('--username', '-u', required=False, help='server username')
    parser.add_argument('--password', '-p', required=False, help='server password.')
    parser.add_argument('--sle-token', '-t', required=False, help='SLE API Token.')
    parser.add_argument(
        '--relax-validation',
        required=False,
        default=False,
        action='store_true',
        help='Relax validation. Only supported by some tests, such as file, '
             + 'which cannot easly validate extra data present on the server.')
    subparsers = parser.add_subparsers(dest='command', required=True)
    subparsers.add_parser('populate', help='populate the server with test data')
    subparsers.add_parser(
        'record',
        help='record the initial state of the server prior to running a restore operation')
    subparsers.add_parser('validate', help='validate the data on the server matches the test data')

    options = parser.parse_args()
    server = options.server
    if options.sle_token:
        if options.username or options.password:
            raise ValueError(
                "Please set either the SLE API Token (--sle-token or -r) or the username/password arguments but not both."
            )
    username = options.username
    password = options.password
    sle_token = options.sle_token
    relax_validation = options.relax_validation

    test = test_class(server, relax_validation, username, password, sle_token)

    if 'populate' == options.command:
        test.populate_data()
    elif 'record' == options.command:
        test.record_initial_data()
    elif 'validate' == options.command:
        test.validate_data()
