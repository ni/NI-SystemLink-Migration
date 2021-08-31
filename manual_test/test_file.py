import argparse
import requests
from requests.auth import HTTPBasicAuth

files = [
            {
                'file': (f'File {i}.txt', f'Contents {i}'),
                'metadata': f'{{"key{i}":"value{i}"}}'
            } for i in range(1, 100)
        ]

upload_route = '/nifile/v1/service-groups/Default/upload-files'
get_route = '/nifile/v1/service-groups/Default/files'


def raise_if_existing_data(server, user, password):
    url = server + get_route
    response = requests.get(url, params={'take': 1}, auth=HTTPBasicAuth(user, password), verify=False)
    if response.status_code == 404:
        return

    response.raise_for_status()
    data = response.json()
    if data['availableFiles']:
        raise Exception('There is existing file data on the server')


def populate_data(server, user, password):
    raise_if_existing_data(server, user, password)
    url = server + upload_route
    for f in files:
        response = requests.post(url, files=f, auth=HTTPBasicAuth(user, password), verify=False)
        response.raise_for_status()


def validate_data(server, user, password):
    print('todo: validate')
    pass


if __name__ == '__main__':
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

    if 'populate' == options.command:
        populate_data(server, username, password)
    elif 'validate' == options.command:
        validate_data(server, username, password)


