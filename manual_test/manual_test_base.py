import argparse
from requests.auth import HTTPBasicAuth
import requests
from urllib.parse import urljoin


class ManualTestBase:
    def __init__(self, server, username, password):
        """
        Constructs the manual test base class.

        :param server: The url of the SystemLink Server, for example https://systemlink.example.com
        :param username: The username to use to log in to the server.
        :param password: The password to use to log in to the server.
        :return: None.
        """

        self._server = server
        self._auth = HTTPBasicAuth(username, password)

    def populate_data(self):
        raise NotImplementedError

    def validate_data(self):
        raise NotImplementedError

    def request(self, method, route, **kwargs):
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

    def get(self, route, **kwargs):
        """
        Sends a get request. See self.request for parameter details.
        """

        return self.request("GET", route, **kwargs)

    def post(self, route, **kwargs):
        """
        Sends a post request. See self.request for parameter details.
        """

        return self.request("POST", route, **kwargs)

    def put(self, route, **kwargs):
        """
        Sends a put request. See self.request for parameter details.
        """

        return self.request("PUT", route, **kwargs)

    def handle_command_line(derived_class):
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
        subparsers.add_parser('validate', help='validate the data on the server matches the test data')

        options = parser.parse_args()
        print(options)
        server = options.server
        username = options.username
        password = options.password

        test = derived_class(server, username, password)

        if 'populate' == options.command:
            test.populate_data()
        elif 'validate' == options.command:
            test.validate_data()
