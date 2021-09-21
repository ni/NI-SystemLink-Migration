from typing import Any, Dict, List, Optional
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'SystemStateManager'
SYSTEM_STATE_DATABASE_NAME = 'nisystemstate'
TEST_NAME = 'SystemStateMigrationTest'
GET_SYSTEM_STATES_ROUTE = 'nisystemsstate/v1/states'
CREATE_SYSTEM_STATE_ROUTE = 'nisystemsstate/v1/states'
PATCH_SYSTEM_STATE_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}'
GET_SYSTEM_STATE_DETAILS_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}'
GET_SYSTEM_STATE_HISTORY_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}/history'
GET_SYSTEM_STATE_BY_VERSION_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}/history/{version}'


class TestSystemStates(ManualTestBase):
    def populate_data(self) -> None:
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace_for_test(self)
        for workspace in workspace_utilities.get_workspaces(self):
            state_id = self.__create_test_state(workspace)
            # Push an update so the state has a non-trivial history
            self.__update_test_state(state_id)

        self.record_json_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            self.__get_all_state_data()
        )

    def record_initial_data(self) -> None:
        self.record_json_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            self.__get_all_state_data()
        )

    def validate_data(self) -> None:
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_json_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_snapshot = self.__get_all_state_data()
        workspaces = WorkspaceUtilities().get_workspaces(self)

        migrated_record_count = 0
        for state_data in current_snapshot:
            expected_state_data = self.find_record_with_matching_id(state_data, source_service_snapshot)
            if expected_state_data is not None:
                self.__assert_state_data_equal(expected_state_data, state_data)
                self.__assert_state_has_valid_workspace(state_data, workspaces)
                migrated_record_count = migrated_record_count + 1
            else:
                # This test does not expect any auto-generated states. It just verifies that if any extra
                # states exist, they were present when the server first started.
                expected_state = self.__find_state_by_name(state_data, target_service_snaphot)
                assert expected_state is not None

        assert len(source_service_snapshot) == migrated_record_count

    def __get_all_state_data(self) -> List[Dict[str, Any]]:
        all_state_ids = self.__get_all_state_ids()
        all_state_data = []
        for id in all_state_ids:
            current_state = self.__get_state_details(id)
            history = self.__get_state_history(id)
            all_versions = self.__get_all_versions_of_state(id, history)
            all_state_data.append({
                'id': id,
                'current': current_state,
                'history': history,
                'all_versions': all_versions,
            })

        return all_state_data

    def __get_all_state_ids(self) -> List[str]:
        response = self.get(GET_SYSTEM_STATES_ROUTE)
        response.raise_for_status()

        # NOTE: This query only returns a sub-set of data for the state.
        states = response.json()['states']
        return [state['id'] for state in states]

    def __get_state_details(self, state_id: str) -> Dict[str, Any]:
        uri = GET_SYSTEM_STATE_DETAILS_ROUTE_FORMAT.format(id=state_id)
        response = self.get(uri)
        response.raise_for_status()

        return response.json()

    def __get_state_history(self, state_id: str) -> Dict[str, Any]:
        uri = GET_SYSTEM_STATE_HISTORY_ROUTE_FORMAT.format(id=state_id)
        response = self.get(uri)
        response.raise_for_status()

        return response.json()

    def __get_all_versions_of_state(self, state_id: str, history: Dict[str, Any]) -> List[Dict[str, Any]]:
        result = []
        for version in [record['version'] for record in history['versions']]:
            uri = GET_SYSTEM_STATE_BY_VERSION_ROUTE_FORMAT.format(id=state_id, version=version)
            response = self.get(uri)
            response.raise_for_status()
            result.append(response.json())

        return result

    def __create_test_state(self, workspace: str) -> str:
        state = {
            'name': f'State for {TEST_NAME} for workspace {workspace}',
            'description': f'This state was created for {TEST_NAME}',
            'distribution': 'WINDOWS',
            'architecture': 'X64',
            'feeds': [self.__build_test_feed()],
            'packages': [self.__build_test_package('initial_package', '1.0')],
            'workspace': workspace
        }
        response = self.post(CREATE_SYSTEM_STATE_ROUTE, retries=self.build_default_400_retry(), json=state)
        response.raise_for_status()

        return response.json()['id']

    def __build_test_feed(self) -> Dict[str, Any]:
        return {
            'name': 'Test Feed',
            'enabled': True,
            'url': 'www.example.com/feed',
            'compressed': True
        }

    def __build_test_package(self, name: str, version: str) -> Dict[str, Any]:
        return {
            'name': name,
            'version': version,
            'installRecommends': True
        }

    def __update_test_state(self, state_id: str):
        packages = [
            self.__build_test_package('initial_package', '1.5'),
            self.__build_test_package('other_package', '3.14')
        ]
        patch = {
            'packages': packages
        }

        uri = PATCH_SYSTEM_STATE_ROUTE_FORMAT.format(id=state_id)
        response = self.patch(uri, json=patch)
        response.raise_for_status()

    def __assert_state_data_equal(self, expected: Dict[str, Any], actual: Dict[str, Any]):
        assert expected == actual

    def __assert_state_has_valid_workspace(self, state_data: Dict[str, Any], workspaces: List[str]):
        current = state_data['current']
        matching_workspace = next((workspace for workspace in workspaces if workspace == current['workspace']), None)
        assert matching_workspace is not None

    def __find_state_by_name(
        self,
        state_data: Dict[str, Any],
        collection: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        name = state_data['current']['name']
        return next((record for record in collection if record['current']['name'] == name))


if __name__ == '__main__':
    handle_command_line(TestSystemStates)
