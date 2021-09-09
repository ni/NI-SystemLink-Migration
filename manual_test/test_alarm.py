import datetime
from typing import Any, Dict, List
from manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'Alarm'
TEST_NAME = 'AlarmMigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
ACKNOWLEDGE_ALARMS_BY_ID_ROUTE = 'nialarm/v1/acknowledge-instances-by-instance-id'
ADD_NOTES_TO_ALARM_ROUTE_FORMAT = 'nialarm/v1//instances/{instance_id}/notes'
CREATE_OR_UPDATE_ALARM_ROUTE = 'nialarm/v1/instances'
DELETE_ALARMS_BY_ID_ROUTE = 'nialarm/v1/delete-instances-by-instance-id'
QUERY_ALARMS_ROUTE = 'nialarm/v1/query-instances'

"""Set this when debugging to cleanup the alarm database prior to populating the server with alarms."""
DEBUG_CLEANUP_EXISTING_DATA = False


class TestAlarm(ManualTestBase):

    def populate_data(self) -> None:
        if DEBUG_CLEANUP_EXISTING_DATA:
            self.__delete_existing_alarms()

        WorkspaceUtilities().create_workspace(TEST_WORKSPACE_NAME, self)
        index = 0
        startTime = datetime.datetime.now()
        for alarm in self.__generate_alarms(startTime):
            instance_id = self.__raise_alarm(alarm)
            self.__add_note(instance_id, startTime + datetime.timedelta(hours=1), index)
            self.__acknowledge_if_needed(alarm, instance_id, startTime + datetime.timedelta(hours=2), index)
            self.__clearIfNeeded(alarm, startTime + datetime.timedelta(hours=3), index)
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

    def __add_note(self, instance_id: str, time: datetime, index: int):
        u = f'nialarm/v1//instances/{instance_id}'
        uri = ADD_NOTES_TO_ALARM_ROUTE_FORMAT.format(instance_id=instance_id)
        note = {
            'note': f'Note #{index}',
            'createdAt': self.datetime_to_string(time)
        }
        response = self.post(uri, json={'notes': [note]})
        response.raise_for_status()

    def __acknowledge_if_needed(
            self,
            alarm: Dict[str, Any],
            instance_id: str,
            time: datetime,
            index: int
    ):
        if self.__need_to_acknowledge(alarm):
            ack = {
                'instanceIds': [instance_id],
                'forceClear': False,
                'note': {
                    'note': f'Acknowledgment #{index}',
                    'createdAt': self.datetime_to_string(time)
                }
            }
            response = self.post(ACKNOWLEDGE_ALARMS_BY_ID_ROUTE, json=ack)
            response.raise_for_status()

    def __clearIfNeeded(self, alarm: Dict[str, Any], time: datetime, index: int):
        if self.__need_to_clear(alarm):
            clear = {
                'alarmId': alarm['alarmId'],
                'workspace': alarm['workspace'],
                'transition': self.__generate_clear_transition(time, index)
            }
            response = self.post(CREATE_OR_UPDATE_ALARM_ROUTE, json=clear)
            response.raise_for_status()

    def __delete_existing_alarms(self):
        instance_ids = [alarm['instanceId'] for alarm in self.__get_all_alarms()]
        if len(instance_ids) > 0:
            response = self.post(DELETE_ALARMS_BY_ID_ROUTE, json={'instanceIds': instance_ids})
            response.raise_for_status()

    def __generate_alarms(self, startTime: datetime) -> List[Dict[str, Any]]:
        alarms = []
        for workspace_id in WorkspaceUtilities().get_workspaces(self):
            alarms.extend(self.__generate_alarms_for_workspace(workspace_id, startTime))
        return alarms

    def __generate_alarms_for_workspace(self, workspace_id: str, startTime: datetime) -> List[Dict[str, Any]]:
        alarms = []
        alarms.append(self.__generate_alarm(workspace_id, startTime, 0, 'Set'))
        alarms.append(self.__generate_alarm(workspace_id, startTime, 1, 'Set.Ack'))
        alarms.append(self.__generate_alarm(workspace_id, startTime, 2, 'Set.Clear'))
        alarms.append(self.__generate_alarm(workspace_id, startTime, 3, 'Set.Ack.Clear'))
        return alarms

    def __generate_alarm(self, workspace_id, startTime: datetime, index: int, mode: str) -> Dict[str, Any]:
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

    def __generate_set_transition(self, time: datetime) -> Dict[str, Any]:
        return {
            'transitionType': 'SET',
            'occuredAt': self.datetime_to_string(time),
            'severityLevel': 1,
            'notificationStrategyIds': [],
            'condition': 'Test Alarm Set',
            'shortText': 'Alarm created for test',
            'detailText': f'This alarm was created for {TEST_NAME}',
            'keywords': [TEST_NAME],
            'properties': {'forTest': 'True'}
        }

    def __generate_clear_transition(self, time: datetime, index: int) -> Dict[str, Any]:
        return {
            'transitionType': 'CLEAR',
            'occuredAt': self.datetime_to_string(time),
            'severityLevel': -1,
            'notificationStrategyIds': [],
            'condition': 'Test Alarm Cleared',
            'shortText': 'Alarm cleared for test',
            'detailText': f'Alarm clear notification #{index}',
            'keywords': [TEST_NAME],
            'properties': {'forTest': 'True'}
        }

    def __need_to_acknowledge(self, alarm: Dict[str, Any]) -> bool:
        return 'Ack' in alarm['alarmId']

    def __need_to_clear(self, alarm: Dict[str, Any]) -> bool:
        return 'Clear' in alarm['alarmId']


if __name__ == '__main__':
    handle_command_line(TestAlarm)
