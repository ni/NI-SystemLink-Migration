from manual_test.manual_test_base import ManualTestBase, handle_command_line, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.file_utilities import FileUtilities, TDMS_PATH
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from datetime import datetime, timedelta
import random
from random import randrange
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

RESULTS_ROUTE='/nitestmonitor/v2/results'
STEPS_ROUTE='/nitestmonitor/v2/steps'
PRODUCTS_ROUTE='/nitestmonitor/v2/products'

class TestTestMonitor(ManualTestBase):
    statuses = [
        {'statusType': 'FAILED', 'statusName': 'Failed'},
        {'statusType': 'PASSED', 'statusName': 'Passed'},
        {'statusType': 'RUNNING', 'statusName': 'Running'},
        {'statusType': 'DONE', 'statusName': 'Done'},
    ]
    parts = ['Product1', 'Product2', 'Product3']

    __datetime_base: Optional[datetime] = None
    __file_utilities = FileUtilities()

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
        self.__create_products(workspaces[0])
        self.__create_results(workspaces)

    def __create_products(self, workspace: str):
        fileId = self.__upload_file(workspace)
        products = [
            {
                'name': f'{part} Name',
                'partNumber': part,
                'family': f'{part}-family',
                'keywords': [f'{part}-keyword-1', f'{part}-keyword-2'],
                'properties': {f'{part}Property': f'{part}Value'},
                'fileIds': [fileId]
            }
            for part in self.parts
        ]

        response = self.post(PRODUCTS_ROUTE, json={'products': products})
        print(response.json())
        response.raise_for_status()

    def __create_results(self, workspaces: List[str]):
        for workspace in workspaces:
            for i in range(10):
                result_id = self.__create_result(workspace)
                self.__create_steps(result_id)

    def __create_result(self, workspace: str):
        programs = ['Program1', 'Program2', 'Program3']
        systems = ['Tester1', 'Tester2', 'Tester3']
        hosts = ['Host1', 'Host2', 'Host3']
        operators = ['Operator1', 'Operator2', 'Operator3']
        keywords = ['keyword1', 'keyword2', 'keyword2', 'keyword4']
        propertyKeys = ['property1', 'property2', 'property3']
        propertyValues =  ['value1', 'value2', 'value3']

        fileId = self.__upload_file(workspace)
        result = {
            'programName': random.choice(programs), 'status': random.choice(self.statuses),
            'systemId': random.choice(systems),
            'hostName': random.choice(hosts),
            'properties': {random.choice(propertyKeys): random.choice(propertyValues)},
            'keywords': [random.choice(keywords), random.choice(keywords)],
            'serialNumber': str(random.randint(111111, 999999)),
            'operator': random.choice(operators),
            'partNumber': random.choice(self.parts),
            'fileIds': [fileId],
            'startedAt': self.__random_date(),
            'totalTimeInSeconds': random.randint(1, 120),
            'workspace': workspace
        }

        response = self.post(RESULTS_ROUTE, json={'results':[result]})
        response.raise_for_status()
        return response.json()['results'][0]['id']

    def __create_steps(self, result_id: str):
        steps = []
        for i in range(1, 6):
            step = self.__create_step(result_id, 'Step ', i)
            for j in range(1, 6):
                nested_step = self.__create_step(result_id, f'Step {i}.', j)
                step['children'].append(nested_step)

            steps.append(step)

        response = self.post(STEPS_ROUTE, json={'steps': steps})
        print(response.json())
        response.raise_for_status()

    def __create_step(self, result_id: str, name: str, index: int) -> Dict[str, Any]:
        return {
            'name': f'{name}{index}',
            'resultId': result_id,
            'stepType': 'SequenceCall',
            'status': random.choice(self.statuses),
            'startedAt': self.__random_date(),
            'totalTimeInSeconds': random.randint(1, 120),
            'dataModel': f'model{index}',
            'data': {
                'text': f'text{index}',
                'parameters': [
                    {f'text{index}.1': f'text{index}.2'},
                    {f'text{index}.3': f'text{index}.4'}
                ]
            },
            'children': []
        }

    def __random_date(self):
        if not self.__datetime_base:
            delta = timedelta(seconds=randrange(20 * 24 * 60 * 60))
            self.__datetime_base = datetime.now() + delta
        self.__datetime_base += timedelta(seconds=randrange(120))
        return self.datetime_to_string(self.__datetime_base)

    def __upload_file(self, workspace: str) -> str:
        response = self.__file_utilities.upload_file(
                self,
                workspace,
                TDMS_PATH)
        uri = response['uri']
        id = urlparse(uri).path.split('/').pop()
        return id

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
