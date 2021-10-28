from typing import Any, Dict, List
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE

SERVICE_NAME = 'UserData'
SERVICE_DATABASE_NAME = 'SystemsManagement'
TEST_NAME = 'SystemsManagementMigrationTest'
SYSTEMS_ROUTE = 'nisysmgmt/v1/systems'


class TestSystemsManagement(ManualTestBase):
    def populate_data(self) -> None:
        self.__create_test_data()

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

        assert current_data_snapshot == source_user_data_snapshot

    def __get_all_systems(self) -> List[Dict[str, Any]]:
        fields_to_capture = ['id', 'connected' 'alias', 'packages', 'feeds', 'workspace']
        response = self.get(SYSTEMS_ROUTE)
        response.raise_for_status()
        raw_systems = response.json()
        systems = []
        for raw_system in raw_systems:
            system = {}
            for field_to_capture in fields_to_capture:
                system[field_to_capture] = raw_system[field_to_capture]
            systems.append(system)
        return systems

    def __create_test_data(self):
        pass


if __name__ == '__main__':
    handle_command_line(TestSystemsManagement)
