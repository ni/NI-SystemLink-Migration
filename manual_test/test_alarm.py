import datetime
from typing import Dict, List
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'Alarm'
TEST_NAME = 'AlarmMigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
ACKNOWLEDGE_ALARMS_BY_ID_ROUTE ='/nialarm/v1/acknowledge-instances-by-instance-id'
ADD_NOTES_TO_ALARM_ROUTE_FORMAT = '/nialarm/v1//instances/{instance_id}/notes'
CREATE_OR_UPDATE_ALARM_ROUTE = '/nialarm/v1/instances'
QUERY_ALARMS_ROUTE = '/nialarm/v1/query-instances'

class TestAlarm(ManualTestBase):

    def populate_data(self) -> None:
        WorkspaceUtilities().create_worksace(self, TEST_WORKSPACE_NAME)
        index = 0
        startTime = datetime.datetime.now()
        for alarm in self.__generate_alarms(startTime):
            self.__raise_alarm(alarm)
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
        response = self.post(QUERY_ALARMS_ROUTE, json={})
        response.raise_for_status()

        return response.json()

    def __generate_alarms(self, startTime) -> List[Dict[str, str]]:
        alarms = []
        for workspace in WorkspaceUtilities().get_workspaces(self):
            alarms.extend(self.__generate_alarms_for_workspace(workspace, startTime))
        return alarms

    def __generate_alarms_for_workspace(self, workspace, startTime) -> List[Dict[str, str]]:
        alarms = []
        time = startTime
        alarms.append(self.__generate_alarm(workspace, time, 0, 'Set'))
        time = time + datetime.timedelta(hours=1)
        alarms.append(self.__generate_alarm(workspace, startTime, 1, 'Set.Ack'))
        time = time + datetime.timedelta(hours=1)
        alarms.append(self.__generate_alarm(workspace, startTime, 2, 'Set.Clear'))
        time = time + datetime.timedelta(hours=1)
        alarms.append(self.__generate_alarm(workspace, startTime, 3, 'Set.Ack.Clear'))

    def __generate_alarm(self, workspace, startTime, index, mode) -> Dict[str, str]:
        channel = f'{TEST_NAME}.{mode}'
        return {
            'alarmId': f'{channel}.{index}',
            'workspace': workspace['id'],
            'transition': self.__generate_set_transition(startTime),
            'channel': channel,
            'resourceType': f'{TEST_NAME} resource',
            'displayName': f'Test alarm #{index}',
            'description': f'Migration Test alarm - mode:{mode}',
            'keywords': [TEST_NAME],
            'properties': {'forTest': 'True'}
        }

    def __generate_set_transition(self, time) -> Dict[str, str]:
        return {
            'transitionType': 'SET',
            'occuredAt': time,
            'severityLevel': 1,
            'notificationStrategyIds': [],
            'condition': 'Test Alarm',
            'shortText': 'Alarm created for test',
            'detailText': f'This alarm was created for {TEST_NAME}',
            'keywords': [TEST_NAME],
            'properties': {'forTest': 'True'}
        }

