from typing import Any, Dict, List
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE

SERVICE_NAME = 'UserData'
SERVICE_DATABASE_NAME = 'niuserdata'
TEST_NAME = 'UserDataMigrationTest'
USER_DATA_ITEMS_ROUTE = 'niuserdata/v1/items'


class TestUserData(ManualTestBase):
    def populate_data(self) -> None:
        self.__create_test_user_data()

        self.record_json_data(
            SERVICE_NAME,
            SERVICE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            self.__get_all_user_data()
        )

    def record_initial_data(self) -> None:
        self.record_json_data(
            SERVICE_NAME,
            SERVICE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            self.__get_all_user_data()
        )

    def validate_data(self) -> None:
        source_user_data_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            SERVICE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_user_data_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            SERVICE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_snapshot = self.__get_all_user_data()

        for user_data in current_snapshot:
            expected_value = self.find_record_with_matching_id(user_data, source_user_data_snapshot)
            if expected_value is not None:
                assert expected_value == user_data
            else:
                expected_value = self.find_record_with_matching_property_value(
                    user_data,
                    target_user_data_snapshot,
                    'user')
                assert expected_value is not None

    def __get_all_user_data(self) -> List[Dict[str, Any]]:
        response = self.get(USER_DATA_ITEMS_ROUTE)
        response.raise_for_status()
        return response.json()['items']

    def __create_test_user_data(self) -> str:
        user_data = [{
            'application': 'fake-application',
            'name': 'name',
            'value': f'User data for {TEST_NAME}',
            'visibleToOthers': 'false',
            'expectedRevision': 0,
            'category': 'test-category',
        }]
        response = self.post(USER_DATA_ITEMS_ROUTE, retries=self.build_default_400_retry(), json=user_data)
        response.raise_for_status()

        return response.json()


if __name__ == '__main__':
    handle_command_line(TestUserData)
