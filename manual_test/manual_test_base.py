import argparse
import datetime
import json
import os
from requests.auth import HTTPBasicAuth
import requests
from typing import Type
from urllib.parse import urljoin
from urllib3 import disable_warnings, exceptions

# Record type for data recorded from a clean server prior to restoring data
CLEAN_SERVER_RECORD_TYPE: str = 'clean'
# Record type for data recorded from a server which is populated with test data
POPULATED_SERVER_RECORD_TYPE: str = 'populated'


class ManualTestBase:

    disable_warnings(exceptions.InsecureRequestWarning)

    def __init__(self, server: str, username: str, password: str) -> None:
        """
        Constructs the manual test base class.

        :param server: The url of the SystemLink Server, for example https://systemlink.example.com
        :param username: The username to use to log in to the server.
        :param password: The password to use to log in to the server.
        :return: None.
        """

        self._server = server
        self._auth = HTTPBasicAuth(username, password)

    def populate_data(self) -> None:
        """
        Derived class should override to populate the SystemLink server with test data.
        """

        raise NotImplementedError

    def record_initial_data(self) -> None:
        """
        Derived class should ovveride to record the initial state of the SystemLink server prior
        to running a restore operation. Recorded data should be used by the validate_data() method.
        """

        raise NotImplementedError

    def validate_data(self) -> None:
        """
        Derived class should override to validate the SystemLink server containst the test
        data added by populate_data. validate_data and populate_data can be called from
        separate processes, so cannot depend on state to validate data.
        """

        raise NotImplementedError

    def request(self, method: str, route: str, **kwargs) -> requests.Response:
        """
        Sends a request.

        :param method: Method for the request. See requests.request.
        :param route: URL for the request, relative to self.server.
        :param kwargs: See requests.request
        """

        return requests.request(
                method,
                urljoin(self._server, route),
                auth=kwargs.pop('auth', self._auth),
                verify=kwargs.pop('verify', False),
                **kwargs)

    def get(self, route: str, **kwargs) -> requests.Response:
        """
        Sends a get request. See self.request for parameter details.
        """

        return self.request('GET', route, **kwargs)

    def post(self, route: str, **kwargs) -> requests.Response:
        """
        Sends a post request. See self.request for parameter details.
        """

        return self.request('POST', route, **kwargs)

    def put(self, route: str, **kwargs) -> requests.Response:
        """
        Sends a put request. See self.request for parameter details.
        """

        return self.request('PUT', route, **kwargs)

    def read_recorded_data(
            self,
            category: str,
            collection: str,
            record_type: str,
            required: bool = True
    ) -> list:
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

    def record_data(self, category: str, collection: str, record_type: str, data) -> None:
        file_path = self.__build_recording_file_path(
            category,
            collection,
            record_type,
            create_folder_if_missing=True)
        with open(file_path, 'w') as file:
            json.dump(data, file)

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

    def datetime_to_string(self, time: datetime) -> str:
        """Converts a datetime object to a string in the format expected by SystemLink"""
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")


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

    test = test_class(server, username, password)

    if 'populate' == options.command:
        test.populate_data()
    elif 'record' == options.command:
        test.record_initial_data()
    elif 'validate' == options.command:
        test.validate_data()
