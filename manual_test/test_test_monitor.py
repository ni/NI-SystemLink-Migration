from manual_test.manual_test_base import ManualTestBase, handle_command_line, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from typing import List

class TestTestMonitor(ManualTestBase):
    def populate_data(self):
        WorkspaceUtilities().create_workspace('WorkspaceForManualTestMonitorMigrationTest', self)
        workspaces = WorkspaceUtilities().get_workspaces(self)
        self.__populate_test_monitor_data(workspaces)
        self.__record_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self):
        """The file service should not be populated with initial data."""
        pass

    def validate_data(self):
        expected_test_monitor_data = self.__read_recorded_data(POPULATED_SERVER_RECORD_TYPE)
        actual_test_monitor_data = self.__get_test_monitor_data()

        self.__assert_test_monitor_data_matches(actual_test_monitor_data, expected_test_monitor_data)

    def __populate_test_monitor_data(self, workspaces: List[str]):
        raise NotImplemented

    def __get_test_monitor_data(self):
        raise NotImplemented

    def __assert_test_monitor_data_matches(self, actual_test_monitor_data, expected_test_monitor_data):
        raise NotImplemented

    def __record_data(self, record_type: str):
        raise NotImplemented

    def __read_recorded_data(self, record_type: str):
        raise NotImplemented


if __name__ == '__main__':
    handle_command_line(TestTestMonitor)
