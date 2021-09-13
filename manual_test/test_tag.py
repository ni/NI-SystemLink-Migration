import datetime
from typing import List, Dict

from manual_test.manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from nislmigrate.logs.migration_error import MigrationError

SERVICE_NAME = 'Tag'
TEST_WORKSPACE_NAME = 'CustomWorkspaceForManualTagMigrationTest'
TAGS_ROUTE = '/nitag/v2/tags/'
TAGS_WITH_VALUES_ROUTE = '/nitag/v2/tags-with-values/'
data_types = ['INT', 'DOUBLE', 'DATE_TIME', 'U_INT64', 'BOOLEAN', 'STRING']
data_type_values_1 = {
    'INT': 0,
    'DOUBLE': 5.5,
    'DATE_TIME': '2021-07-07T00:00:00.0000000Z',
    'U_INT64': 3000000000,
    'BOOLEAN': False,
    'STRING': 'test string'
}
data_type_values_2 = {
    'INT': 50,
    'DOUBLE': 5.7,
    'DATE_TIME': '2021-06-06T00:00:00.0000000Z',
    'U_INT64': 3000000002,
    'BOOLEAN': True,
    'STRING': 'test string 2'
}
expected_mins = {
    'INT': '0',
    'DOUBLE': '5.5',
    'DATE_TIME': None,
    'U_INT64': '3000000000',
    'BOOLEAN': None,
    'STRING': None
}
expected_maxs = {
    'INT': '50',
    'DOUBLE': '5.7000000000000002',
    'DATE_TIME': None,
    'U_INT64': '3000000002',
    'BOOLEAN': None,
    'STRING': None
}
expected_averages = {
    'INT': 25.0,
    'DOUBLE': 5.6,
    'DATE_TIME': 'NaN',
    'U_INT64': 3000000001,
    'BOOLEAN': 'NaN',
    'STRING': 'NaN'
}
expected_counts = {
    'INT': 2,
    'DOUBLE': 2,
    'DATE_TIME': 2,
    'U_INT64': 2,
    'BOOLEAN': 2,
    'STRING': 2
}


class TestTag(ManualTestBase):

    def populate_data(self) -> None:
        WorkspaceUtilities().create_workspace(TEST_WORKSPACE_NAME, self)
        for tag in self.__generate_tags_data():
            self.__upload_tag(tag)
            now = datetime.datetime.now()
            self.__update_tag_value(tag, data_type_values_1[tag['type']], now)
            self.__update_tag_value(tag, data_type_values_2[tag['type']], now + datetime.timedelta(days=1))
        self.record_data(SERVICE_NAME, 'tag_data', POPULATED_SERVER_RECORD_TYPE, self.__get_all_tags())

    def record_initial_data(self) -> None:
        self.record_data(SERVICE_NAME, 'tag_data', CLEAN_SERVER_RECORD_TYPE, self.__get_all_tags())

    def validate_data(self) -> None:
        all_tags = self.__get_all_tags()
        clean_server_tags = self.read_recorded_data(
            SERVICE_NAME,
            'tag_data',
            CLEAN_SERVER_RECORD_TYPE,
            required=True)
        populated_server_tags = self.read_recorded_data(
            SERVICE_NAME,
            'tag_data',
            CLEAN_SERVER_RECORD_TYPE,
            required=True)

        for tag in all_tags:
            expected_tag = self.__find_matching_record(tag, populated_server_tags)
            if expected_tag is not None:
                self.__validate_tag(tag, expected_tag)
                self.__validate_current_tag_value(tag, data_type_values_2[expected_tag['type']])
            else:
                expected_tag = self.__find_matching_record(tag, clean_server_tags)
                self.__validate_tag(tag, expected_tag)

        for expected in self.__generate_tags_data():
            self.__validate_current_tag_aggregates(expected)

    @staticmethod
    def __find_matching_record(record, collection: List):
        return next((item for item in collection if item['id'] == record['id']), None)

    def __get_all_tags(self) -> list:
        response = self.get(TAGS_ROUTE)
        response.raise_for_status()
        return response.json()['tags']

    @staticmethod
    def __validate_tag(tag, expected):
        print('Validating tag: ' + tag['workspace'] + '/' + tag['path'])
        assert tag['path'] == expected['path']
        assert tag['type'] == expected['type']
        assert tag['keywords'] == expected['keywords']
        assert tag['properties'] == expected['properties']
        assert tag['collectAggregates'] == expected['collectAggregates']
        assert tag['workspace'] == expected['workspace']
        print('Done validating tag')

    def __validate_current_tag_value(self, tag, expected_value):
        print('Validating tag value: ' + tag['workspace'] + '/' + tag['path'])
        values = self.__get_tag_values_json_from_server(tag)
        try:
            assert values['current']['value']['value'] == str(expected_value)
        except AssertionError:
            assert float(values['current']['value']['value']) == float(expected_value)
        print('Done validating tag value')

    def __upload_tag(self, tag):
        url = TAGS_ROUTE + tag['workspace'] + '/' + tag['path']
        print('Uploading tag to: ' + url)
        response = self.put(url, json=tag)
        response.raise_for_status()
        print('Done uploading tag')

    def __generate_tags_data(self) -> List[Dict[str, str]]:
        tag_data = [self.__generate_tag_data('tag-' + d, 'Default', d) for d in data_types]
        tag_data.extend([self.__generate_tag_data('tag-' + d, TEST_WORKSPACE_NAME, d) for d in data_types])
        return tag_data

    def __generate_tag_data(self, name: str, workspace_name: str, datatype: str):
        workspace_id = WorkspaceUtilities().get_workspace_id(workspace_name, self)
        if not workspace_id:
            raise MigrationError(workspace_name + ' is not a workspace that has been created yet.')

        return {
            'type': datatype,
            'path': name,
            'keywords': [],
            'properties': {'nitagRetention': 'COUNT'},
            'collectAggregates': True,
            'workspace':  workspace_id
        }

    def __update_tag_value(self, tag, value, time):
        url = TAGS_ROUTE + tag['workspace'] + '/' + tag['path'] + '/values/current'
        print('Updating tag value at: ' + url)
        updated_value = {
            'type': tag['type'],
            'value': value,
        }
        json = {'value': updated_value, 'timestamp': self.datetime_to_string(time)}
        response = self.put(url, json=json)
        response.raise_for_status()
        print('Done updating tag value')

    def __get_tag_json_from_server(self, tag):
        url = TAGS_ROUTE + tag['workspace'] + '/' + tag['path']
        response = self.get(url)
        response.raise_for_status()
        return response.json()

    def __get_tag_values_json_from_server(self, tag):
        url = TAGS_WITH_VALUES_ROUTE + tag['workspace'] + '/' + tag['path']
        response = self.get(url)
        response.raise_for_status()
        return response.json()

    def __validate_current_tag_aggregates(self, tag):
        values = self.__get_tag_values_json_from_server(tag)
        aggregates = values['aggregates']
        assert expected_mins[tag['type']] == aggregates['min']
        assert expected_maxs[tag['type']] == aggregates['max']
        assert expected_averages[tag['type']] == aggregates['avg']
        assert expected_counts[tag['type']] == aggregates['count']


if __name__ == '__main__':
    handle_command_line(TestTag)
