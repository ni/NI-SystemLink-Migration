from typing import Any, Dict, List
from manual_test_base import ManualTestBase, handle_command_line, POPULATED_SERVER_RECORD_TYPE

SERVICE_NAME = 'UserData'
SERVICE_DATABASE_NAME = 'SystemsManagement'
TEST_NAME = 'SystemsManagementMigrationTest'
SYSTEMS_ROUTE = 'nisysmgmt/v1/systems'


class TestSystemsManagement(ManualTestBase):
    def populate_data(self) -> None:
        # This test requires manually connecting a real client system
        # instead of being able to automatically populate data.
        # See the README for specific instructions on running this test.
        self.record_json_data(
            SERVICE_NAME,
            SERVICE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            self.__get_all_systems()
        )

    def record_initial_data(self) -> None:
        pass

    def validate_data(self) -> None:
        current_data_snapshot = self.__get_all_systems()
        source_user_data_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            SERVICE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        current_systems = self.__get_data_to_compare_from_systems(current_data_snapshot)
        source_systems = self.__get_data_to_compare_from_systems(source_user_data_snapshot)
        assert current_systems == source_systems

    def __get_all_systems(self) -> List[Dict[str, Any]]:
        response = self.get(SYSTEMS_ROUTE)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def __get_data_to_compare_from_systems(raw_systems) -> List[Dict[str, Any]]:
        fields_to_capture = ['id', 'connected' 'alias', 'packages', 'feeds', 'workspace']
        return [
            {field_to_capture: raw_system[field_to_capture] for field_to_capture in fields_to_capture}
            for raw_system in raw_systems
        ]


if __name__ == '__main__':
    handle_command_line(TestSystemsManagement)
