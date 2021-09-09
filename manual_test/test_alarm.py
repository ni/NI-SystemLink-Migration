import datetime
from typing import Any, Dict, List
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'Alarm'
TEST_NAME = 'AlarmMigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
ACKNOWLEDGE_ALARMS_BY_ID_ROUTE = '/nialarm/v1/acknowledge-instances-by-instance-id'
ADD_NOTES_TO_ALARM_ROUTE_FORMAT = '/nialarm/v1//instances/{instance_id}/notes'
CREATE_OR_UPDATE_ALARM_ROUTE = '/nialarm/v1/instances'
DELETE_ALARMS_BY_ID_ROUTE = '/nialarm/v1/delete-instances-by-instance-id'
QUERY_ALARMS_ROUTE = '/nialarm/v1/query-instances'

"""Set this when debugging to cleanup the alarm database prior to populating the server with alarms."""
DEBUG_CLEANUP_EXISTING_DATA = True


class TestAlarm(ManualTestBase):

    def populate_data(self) -> None:
        if DEBUG_CLEANUP_EXISTING_DATA:
            self.__delete_existing_alarms()

        WorkspaceUtilities().create_workspace(TEST_WORKSPACE_NAME, self)
        index = 0
        startTime = datetime.datetime.now()
        for alarm in self.__generate_alarms(startTime):
            instance_id = self.__raise_alarm(alarm)
            # self.__add_note(index)
            # self.__acknowledgeIfNeeded(alarm, index)
            # self.__clearIfNeeded(alarm, index)
            index = index + 1

        self.record_data(SERVICE_NAME, 'nialarms', POPULATED_SERVER_RECORD_TYPE, self.__get_all_alarms())

    def record_initial_data(self) -> None:
        self.record_data(SERVICE_NAME, 'nialarms', CLEAN_SERVER_RECORD_TYPE, self.__get_all_alarms())

    def validate_data(self) -> None:
        raise NotImplementedError

    def __get_all_alarms(self):
        query = {
            'workspaces': ['*']
        }
        response = self.post(QUERY_ALARMS_ROUTE, json=query)
        response.raise_for_status()

        return response.json()['filterMatches']

    def __raise_alarm(self, alarm: Dict[str, any]) -> str:
        response = self.post(CREATE_OR_UPDATE_ALARM_ROUTE, json=alarm)
        response.raise_for_status()
        return response.json()['instanceId']

    def __delete_existing_alarms(self):
        instance_ids = [alarm['instanceId'] for alarm in self.__get_all_alarms()]
        if len(instance_ids) > 0:
            response = self.post(DELETE_ALARMS_BY_ID_ROUTE, json={'instanceIds': instance_ids})
            response.raise_for_status()

    def __generate_alarms(self, startTime) -> List[Dict[str, Any]]:
        alarms = []
        for workspace_id in WorkspaceUtilities().get_workspaces(self):
            alarms.extend(self.__generate_alarms_for_workspace(workspace_id, startTime))
        return alarms

    def __generate_alarms_for_workspace(self, workspace_id, startTime) -> List[Dict[str, Any]]:
        alarms = []
        time = startTime
        alarms.append(self.__generate_alarm(workspace_id, time, 0, 'Set'))
        time = time + datetime.timedelta(hours=1)
        alarms.append(self.__generate_alarm(workspace_id, startTime, 1, 'Set.Ack'))
        time = time + datetime.timedelta(hours=1)
        alarms.append(self.__generate_alarm(workspace_id, startTime, 2, 'Set.Clear'))
        time = time + datetime.timedelta(hours=1)
        alarms.append(self.__generate_alarm(workspace_id, startTime, 3, 'Set.Ack.Clear'))
        return alarms

    def __generate_alarm(self, workspace_id, startTime, index, mode) -> Dict[str, Any]:
        channel = f'{TEST_NAME}.{mode}'
        return {
            'alarmId': f'{channel}.{index}',
            'workspace': workspace_id,
            'transition': self.__generate_set_transition(startTime),
            'channel': channel,
            'resourceType': f'{TEST_NAME} resource',
            'displayName': f'Test alarm #{index}',
            'description': f'Migration Test alarm - mode:{mode}',
            'keywords': [TEST_NAME],
            'properties': {'forTest': 'True'}
        }

    def __generate_set_transition(self, time) -> Dict[str, Any]:
        return {
            'transitionType': 'SET',
            'occuredAt': self.datetime_to_string(time),
            'severityLevel': 1,
            'notificationStrategyIds': [],
            'condition': 'Test Alarm',
            'shortText': 'Alarm created for test',
            'detailText': f'This alarm was created for {TEST_NAME}',
            'keywords': [TEST_NAME],
            'properties': {'forTest': 'True'}
        }


if __name__ == '__main__':
    handle_command_line(TestAlarm)
