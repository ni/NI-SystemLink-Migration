from typing import Any, Dict, List, Optional
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'SystemStateManager'
SYSTEM_STATE_DATABASE_NAME = 'nisystemstate'
TEST_NAME = 'SystemStateMigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
GET_SYSTEM_STATES_ROUTE = 'nisystemsstate/v1/states'
CREATE_SYSTEM_STATE_ROUTE = 'nisystemsstate/v1/states'
PATCH_SYSTEM_STATE_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}'
GET_SYSTEM_STATE_DETAILS_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}'
GET_SYSTEM_STATE_HISTORY_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}/history'
GET_SYSTEM_STATE_BY_VERSION_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}/history/{version}'


class TestSystemStates(ManualTestBase):
    def populate_data(self) -> None:
        workspace_utilities = WorkspaceUtilities()
        WorkspaceUtilities().create_workspace(TEST_WORKSPACE_NAME, self)
        for workspace in workspace_utilities.get_workspaces(self):
            state_id = self.__create_test_state(workspace)
            self.__update_test_state(state_id)

        self.record_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            self.__get_all_state_data()
        )

    def record_initial_data(self) -> None:
        self.record_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            self.__get_all_state_data()
        )

    def validate_data(self) -> None:
        source_service_snapshot = self.read_recorded_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_snapshot = self.__get_all_state_data()
        current_states = current_snapshot['current_versions']
        histories = current_snapshot['histories']
        v1_states = current_snapshot['v1_states']
        workspaces = WorkspaceUtilities().get_workspaces(self)

        migrated_record_count = 0
        for state in current_states:
            expected_state = self.find_record_with_matching_id(state, source_service_snapshot['current_versions'])
            if expected_state is not None:
                self.__assert_states_equal(expected_state, state)
                self.__assert_state_has_valid_workspace(state, workspaces)
                self.__assert_histories_equal(
                    state['id'],
                    source_service_snapshot['histories'],
                    histories
                )
                self.__assert_v1_states_equal(
                    state['id'],
                    source_service_snapshot['v1_states'],
                    v1_states
                )
                migrated_record_count = migrated_record_count + 1
            else:
                # This test does not expect any auto-generated states. It just verifies that if any extra
                # states exist, they were present when the server first started.
                expected_state = self.__find_state_by_name(state, target_service_snaphot['current_versions'])
                assert expected_state is not None

        assert len(source_service_snapshot['current_versions']) == migrated_record_count

    def __get_all_state_data(self) -> Dict[str, Any]:
        all_state_ids = self.__get_all_state_ids()
        all_states = self.__get_state_details(all_state_ids)
        histories = self.__get_state_histories(all_state_ids)
        v1_states = self.__get_v1_states(histories)

        return {
            'current_versions': all_states,
            'histories': histories,
            'v1_states': v1_states
        }

    def __get_all_state_ids(self) -> List[str]:
        response = self.get(GET_SYSTEM_STATES_ROUTE)
        response.raise_for_status()

        # NOTE: This query only returns a sub-set of data for the state.
        states = response.json()['states']
        return [state['id'] for state in states]

    def __get_state_details(self, state_ids: List[str]) -> List[Dict[str, Any]]:
        result = []
        for id in state_ids:
            uri = GET_SYSTEM_STATE_DETAILS_ROUTE_FORMAT.format(id=id)
            response = self.get(uri)
            response.raise_for_status()
            result.append(response.json())

        return result

    def __get_state_histories(self, state_ids: List[str]) -> List[Dict[str, Any]]:
        result = []
        for id in state_ids:
            uri = GET_SYSTEM_STATE_HISTORY_ROUTE_FORMAT.format(id=id)
            response = self.get(uri)
            response.raise_for_status()

            # NOTE: The history response does not repeat the state ID. So append it
            # to make future lookup easier.
            history = response.json()
            result.append({
                'id': id,
                'history': history
            })

        return result

    def __get_v1_states(self, histories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        result = []
        for history in histories:
            id = history['id']
            v1_version = history['history']['versions'][0]['version']
            uri = GET_SYSTEM_STATE_BY_VERSION_ROUTE_FORMAT.format(id=id, version=v1_version)
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
        response = self.post(CREATE_SYSTEM_STATE_ROUTE, json=state)
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

    def __assert_states_equal(self, expected: Dict[str, Any], actual: Dict[str, Any]):
        assert expected == actual

    def __assert_state_has_valid_workspace(self, state: Dict[str, Any], workspaces: List[str]):
        matching_workspace = next((workspace for workspace in workspaces if workspace == state['workspace']), None)
        assert matching_workspace is not None

    def __assert_histories_equal(
        self,
        state_id: str,
        expected_histories: List[Dict[str, Any]],
        actual_histories: List[Dict[str, Any]]
    ):
        actual_history = self.find_record_by_id(state_id, actual_histories)
        assert actual_history is not None
        expected_history = self.find_record_by_id(state_id, expected_histories)
        assert actual_history == expected_history

    def __assert_v1_states_equal(
        self,
        state_id: str,
        expected_v1_states: List[Dict[str, Any]],
        actual_v1_states: List[Dict[str, Any]]
    ):
        actual_state = self.find_record_by_id(state_id, actual_v1_states)
        assert actual_state is not None
        expected_state = self.find_record_by_id(state_id, expected_v1_states)
        self.__assert_states_equal(expected_state, actual_state)

    def __find_state_by_name(
        self,
        state: Dict[str, Any],
        collection: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return self.find_record_with_matching_property_value(state, collection, 'name')


if __name__ == '__main__':
    handle_command_line(TestSystemStates)
