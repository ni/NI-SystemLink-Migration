import datetime
from typing import Any, Dict, List, Optional
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'SystemStateManager'
SYSTEM_STATE_DATABASE_NAME = 'nisystemstate'
TEST_NAME = 'SystemStateMigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
GET_SYSTEM_STATES_ROUTE = 'nisystemsstate/v1/states'
CREATE_SYSTEM_STATES_ROUTE = 'nisystemsstate/v1/states'
GET_SYSTEM_STATE_DETAILS_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}'
GET_SYSTEM_STATE_HISTORY_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}/history'
GET_SYSTEM_STATE_BY_VERSION_ROUTE_FORMAT = 'nisystemsstate/v1/states/{id}/history/{version}'


class TestSystemStates(ManualTestBase):

    def populate_data(self) -> None:
        pass

    def record_initial_data(self) -> None:
        self.record_data(
            SERVICE_NAME,
            SYSTEM_STATE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            self.__get_all_state_data()
        )

    def validate_data(self) -> None:
        pass

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

    def __get_all_state_ids(self) -> List[Dict[str, Any]]:
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

    def __get_v1_states(self, histories: List[str]) -> List[Dict[str, Any]]:
        result = []
        for history in histories:
            id = history['id']
            v1_version = history['history']['versions'][0]['version']
            uri = GET_SYSTEM_STATE_BY_VERSION_ROUTE_FORMAT.format(id=id, version=v1_version)
            response = self.get(uri)
            response.raise_for_status()
            result.append(response.json())

        return result


if __name__ == '__main__':
    handle_command_line(TestSystemStates)
