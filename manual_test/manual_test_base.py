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

    def __init__(self, server: str, username: str, password: str, relax_validation: bool) -> None:
        """
        Constructs the manual test base class.

        :param server: The url of the SystemLink Server, for example https://systemlink.example.com
        :param username: The username to use to log in to the server.
        :param password: The password to use to log in to the server.
        :param relax_validation: Relax validation for tests that cannot easily validate extra data.
        :return: None.
        """

        self._server = server
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

            return session.request(
                    method,
                    urljoin(self._server, route),
                    auth=kwargs.pop('auth', self._auth),
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

    def get_all_with_continuation_token(self, route: str, data_key: str) -> List[Dict[str, Any]]:
        data, continuation_token = self.__get_data_and_continuation_token(route, data_key, None)
        while continuation_token:
            additional_data, continuation_token = self.__get_data_and_continuation_token(
                route, data_key, continuation_token)
            data.extend(additional_data)

        return data

    def __get_data_and_continuation_token(
        self,
        route: str,
        data_key: str,
        continuation_token: Optional[str]
    ) -> Tuple[List[Dict[str, Any]], str]:
        params = {} if not continuation_token else {'continuationToken': continuation_token}
        response = self.get(route, params=params)
        response.raise_for_status()
        data = response.json()
        return data[data_key], data.get('continuationToken', None)

    def build_default_400_retry(self, rout='POST') -> Retry:
        """
        Builds a standard Retry object for retrying 400 errors on a route.

        This is necessary due to a caching issue encountered by tests that create
        new workspaces. For a short window after the workspace is created, the auth
        token will not have refreshed and operations that reference the workspace will
        fail.
        """
        return Retry(total=5, backoff_factor=2, status_forcelist=[400], allowed_methods=['PUT'])

    def read_recorded_data(
            self,
            category: str,
            collection: str,
            record_type: str,
            required: bool = True
    ) -> List[Dict[str, Any]]:
        file_path = self.__build_recording_file_path(
            category,
            collection,
            record_type,
            create_folder_if_missing=False)

        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception:
            if required:
                msg = f'Unable to read recording file for category="{category}"; collection="{collection}"'
                raise RuntimeError(msg)

        return []

    def record_data(self, category: str, collection: str, record_type: str, data: List[Dict[str, Any]]) -> None:
        file_path = self.__build_recording_file_path(
            category,
            collection,
            record_type,
            create_folder_if_missing=True)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    def __build_recording_file_path(
            self,
            category: str,
            collection: str,
            record_type: str,
            create_folder_if_missing: bool
    ) -> str:
        folder_path = os.path.join(os.getcwd(), '.test', category)
        if create_folder_if_missing:
            os.makedirs(folder_path, exist_ok=True)

        filename = collection + '.' + record_type + '.json'
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
    parser.add_argument('--username', '-u', required=True, help='server username')
    parser.add_argument('--password', '-p', required=True, help='server password.')
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
    username = options.username
    password = options.password
    relax_validation = options.relax_validation

    test = test_class(server, username, password, relax_validation)

    if 'populate' == options.command:
        test.populate_data()
    elif 'record' == options.command:
        test.record_initial_data()
    elif 'validate' == options.command:
        test.validate_data()
