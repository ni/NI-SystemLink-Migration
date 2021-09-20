import datetime
from typing import List, Dict, Any, Optional

from manual_test.manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities, TEST_WORKSPACE_NAME
from nislmigrate.logs.migration_error import MigrationError

SERVICE_NAME = 'Tag'
TAGS_ROUTE = '/nitag/v2/tags/'
TAGS_WITH_VALUES_ROUTE = '/nitag/v2/tags-with-values/'
TAG_HISTORY_ROUTE = '/nitaghistorian/v2/tags/query-history'
TEST_DATE = datetime.datetime(2020, 9, 14)
RECORDED_DATA_IDENTIFIER = 'tag_data'
ALL_DATA_TYPES = ['INT', 'DOUBLE', 'DATE_TIME', 'U_INT64', 'BOOLEAN', 'STRING']
EXPECTED_VALUES_BY_DATATYPE_1 = {
    'INT': 0,
    'DOUBLE': 5.5,
    'DATE_TIME': '2021-07-07T00:00:00.0000000Z',
    'U_INT64': 3000000000,
    'BOOLEAN': False,
    'STRING': 'test string'
}
EXPECTED_VALUES_BY_DATATYPE_2 = {
    'INT': 50,
    'DOUBLE': 5.7,
    'DATE_TIME': '2021-06-06T00:00:00.0000000Z',
    'U_INT64': 3000000002,
    'BOOLEAN': True,
    'STRING': 'test string 2'
}
EXPECTED_MINS = {
    'INT': '0',
    'DOUBLE': '5.5',
    'DATE_TIME': None,
    'U_INT64': '3000000000',
    'BOOLEAN': None,
    'STRING': None
}
EXPECTED_MAXS = {
    'INT': '50',
    'DOUBLE': '5.7000000000000002',
    'DATE_TIME': None,
    'U_INT64': '3000000002',
    'BOOLEAN': None,
    'STRING': None
}
EXPECTED_AVERAGES = {
    'INT': 25.0,
    'DOUBLE': 5.6,
    'DATE_TIME': 'NaN',
    'U_INT64': 3000000001,
    'BOOLEAN': 'NaN',
    'STRING': 'NaN'
}
EXPECTED_COUNTS = {
    'INT': 2,
    'DOUBLE': 2,
    'DATE_TIME': 2,
    'U_INT64': 2,
    'BOOLEAN': 2,
    'STRING': 2
}


class TestTag(ManualTestBase):

    def populate_data(self) -> None:
        WorkspaceUtilities().create_workspace_for_test(self)
        self.__generate_tag_data_on_server()
        self.__record_populated_server_tags()

    def record_initial_data(self) -> None:
        self.__record_clean_server_tags()

    def validate_data(self) -> None:
        self.__validate_read_tag_data_matches()
        self.__validate_generated_tag_history_and_aggregates()

    def __generate_tag_data_on_server(self):
        for tag in self.__generate_tags_data():
            self.__upload_tag(tag)
            tag_type = tag['type']
            expected_value_1 = EXPECTED_VALUES_BY_DATATYPE_1[tag_type]
            expected_value_2 = EXPECTED_VALUES_BY_DATATYPE_2[tag_type]
            self.__update_tag_value(tag, expected_value_1, TEST_DATE)
            self.__update_tag_value(tag, expected_value_2, TEST_DATE + datetime.timedelta(days=1))

    def __get_all_tags(self) -> list:
        response = self.get(TAGS_ROUTE)
        response.raise_for_status()
        return response.json()['tags']

    @staticmethod
    def __are_equal(expected_value, value):
        try:
            assert str(value) == str(expected_value)
            return True
        except AssertionError:
            try:
                return float(value) == float(expected_value)
            except ValueError:
                return True

    def __upload_tag(self, tag):
        url = TAGS_ROUTE + tag['workspace'] + '/' + tag['path']
        print('Uploading tag to: ' + url)
        response = self.put(url, json=tag)
        response.raise_for_status()
        print('Done uploading tag')

    def __generate_tags_data(self) -> List[Dict[str, str]]:
        tag_data = [self.__generate_tag_data('tag-' + d, 'Default', d) for d in ALL_DATA_TYPES]
        tag_data.extend([self.__generate_tag_data('tag-' + d, TEST_WORKSPACE_NAME, d) for d in ALL_DATA_TYPES])
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
        tag_type = tag['type']
        assert EXPECTED_MINS[tag_type] == aggregates['min']
        assert EXPECTED_MAXS[tag_type] == aggregates['max']
        assert EXPECTED_AVERAGES[tag_type] == aggregates['avg']
        assert EXPECTED_COUNTS[tag_type] == aggregates['count']

    def __validate_tag_history(self, tag, expected_value_1, expected_value_2):
        print('Validating tag history: ' + tag['workspace'] + '/' + tag['path'])
        value_history = self.__query_tag_history(tag)
        for timed_value in value_history:
            value = timed_value['value']
            assert self.__are_equal(expected_value_1, value) or self.__are_equal(expected_value_2, value)
        print('Done validating tag history')

    def __validate_read_tag_data_matches(self):
        all_tags = self.__get_all_tags()
        clean_server_tags = self.__read_clean_server_tags()
        populated_server_tags = self.__read_populated_server_tags()
        for tag in all_tags:
            expected_tag = self.find_record_with_matching_path(tag, populated_server_tags)
            if expected_tag is not None:
                self.__validate_tag(tag, expected_tag, True)
            else:
                expected_tag = self.find_record_with_matching_path(tag, clean_server_tags)
                self.__validate_tag(tag, expected_tag, False)

    @staticmethod
    def __validate_tag(tag, expected, exact: bool):
        print('Validating tag: ' + tag['workspace'] + '/' + tag['path'])
        if exact:
            assert tag == expected
        else:
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
        assert self.__are_equal(expected_value, values['current']['value']['value'])
        print('Done validating tag value')

    def __validate_generated_tag_history_and_aggregates(self):
        for generated_tag in self.__generate_tags_data():
            tag_type = generated_tag['type']
            expected_value_1 = EXPECTED_VALUES_BY_DATATYPE_1[tag_type]
            expected_value_2 = EXPECTED_VALUES_BY_DATATYPE_2[tag_type]
            self.__validate_current_tag_value(generated_tag, expected_value_2)
            self.__validate_tag_history(generated_tag, expected_value_1, expected_value_2)
            self.__validate_current_tag_aggregates(generated_tag)

    def __query_tag_history(self, tag):
        json = {
            'path': tag['path'],
            'workspace': tag['workspace'],
            'sortOrder': 'ASCENDING'
        }
        response = self.post(TAG_HISTORY_ROUTE, json=json)
        response.raise_for_status()
        return response.json()['values']

    def find_record_with_matching_path(
            self,
            source: Dict[str, Any],
            collection: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return self.find_record_with_matching_property_value(source, collection, 'path')

    def __record_clean_server_tags(self):
        data = self.__get_all_tags()
        self.record_data(
            SERVICE_NAME,
            RECORDED_DATA_IDENTIFIER,
            CLEAN_SERVER_RECORD_TYPE,
            data)

    def __record_populated_server_tags(self):
        data = self.__get_all_tags()
        self.record_data(
            SERVICE_NAME,
            RECORDED_DATA_IDENTIFIER,
            POPULATED_SERVER_RECORD_TYPE,
            data)

    def __read_clean_server_tags(self):
        return self.read_recorded_data(
            SERVICE_NAME,
            RECORDED_DATA_IDENTIFIER,
            CLEAN_SERVER_RECORD_TYPE,
            required=True)

    def __read_populated_server_tags(self):
        return self.read_recorded_data(
            SERVICE_NAME,
            RECORDED_DATA_IDENTIFIER,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)


if __name__ == '__main__':
    handle_command_line(TestTag)
