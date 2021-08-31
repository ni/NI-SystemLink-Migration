from requests.auth import HTTPBasicAuth
import requests
import urllib


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

    def request(self, method, route, **kwargs):
        """
        Sends a request.

        :param method: Method for the request. See requests.request.
        :param route: URL for the request, relative to self.server.
        :param kwargs: See requests.request
        """

        return requests.request(
                urllib.join(self._server, route),
                auth=kwargs.pop('auth', self._auth),
                verify=kwargs.pop('verify', False),
                **kwargs)

    def get(self, route, **kwargs):
        """
        Sends a get request. See self.request for parameter details.
        """

        return self.request("GET", route, kwargs)

    def post(self, route, **kwargs):
        """
        Sends a post request. See self.request for parameter details.
        """

        return self.request("POST", route, kwargs)

    def put(self, route, **kwargs):
        """
        Sends a put request. See self.request for parameter details.
        """

        return self.request("PUT", route, kwargs)
