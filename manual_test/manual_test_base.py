import argparse
import json
import os
from requests.auth import HTTPBasicAuth
import requests
from typing import Type
from urllib.parse import urljoin
from urllib3 import disable_warnings, exceptions


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

    def capture_initial_data(self) -> None:
        """
        Derived class should ovveride to capture the initial state of the SystemLink server prior
        to running a restore operation. Captured data should be used by the validate_data() method.
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

        return self.request("GET", route, **kwargs)

    def post(self, route: str, **kwargs) -> requests.Response:
        """
        Sends a post request. See self.request for parameter details.
        """

        return self.request("POST", route, **kwargs)

    def put(self, route: str, **kwargs) -> requests.Response:
        """
        Sends a put request. See self.request for parameter details.
        """

        return self.request("PUT", route, **kwargs)

    def read_capture_file(self, category: str, collection: str) -> dict:
        file_path = self.__build_capture_file_path(category, collection, create_folder_if_missing=False)

        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except Exception:
            raise RuntimeError(f'Unable to read capture file found for category=\'{category}\'; collection=\'{collection}\'')

    def write_capture_file(self, category: str, collection: str, data) -> None:
        file_path = self.__build_capture_file_path(category, collection, create_folder_if_missing=True)
        with open(file_path, 'w') as file:
            json.dump(data, file)

    def __build_capture_file_path(self, category: str, collection: str, create_folder_if_missing: bool) -> str:
        folder_path = os.path.join(os.getcwd(), '.test', category)
        if create_folder_if_missing:
            os.makedirs(folder_path, exist_ok=True)
        
        return os.path.join(folder_path, collection + '.json')



def handle_command_line(test_class: Type[ManualTestBase]) -> None:
    """
    Parses command line arguments, instantiates a test class,
    and populates or verifies data.

    :param derived_class: The test class to instantiate
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', required=True, help='systemlink server url. eg https://server')
    parser.add_argument('--username', '-u', required=True, help='server username')
    parser.add_argument('--password', '-p', required=True, help='server password.')
    subparsers = parser.add_subparsers(dest='command', required=True)
    subparsers.add_parser('populate', help='populate the server with test data')
    subparsers.add_parser('capture', help='capture the initial state of the server prior to running a restore operation')
    subparsers.add_parser('validate', help='validate the data on the server matches the test data')

    options = parser.parse_args()
    server = options.server
    username = options.username
    password = options.password

    test = test_class(server, username, password)

    if 'populate' == options.command:
        test.populate_data()
    elif 'capture' == options.command:
        test.capture_initial_data()
    elif 'validate' == options.command:
        test.validate_data()
