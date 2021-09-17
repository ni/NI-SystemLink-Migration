from manual_test.manual_test_base import ManualTestBase, handle_command_line, POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.file_utilities import FileUtilities, TDMS_PATH
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

RESULTS_ROUTE = '/nitestmonitor/v2/results'
STEPS_ROUTE = '/nitestmonitor/v2/steps'
PRODUCTS_ROUTE = '/nitestmonitor/v2/products'
PATHS_ROUTE = '/nitestmonitor/v2/paths'

CATEGORY = 'test_monitor'


class TestTestMonitor(ManualTestBase):
    statuses = [
        {'statusType': 'FAILED', 'statusName': 'Failed'},
        {'statusType': 'PASSED', 'statusName': 'Passed'},
        {'statusType': 'RUNNING', 'statusName': 'Running'},
        {'statusType': 'DONE', 'statusName': 'Done'},
    ]
    parts = ['Product1', 'Product2', 'Product3']
    times = [1.3, 2.4, 8.9, 5.2]

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
        self.__validate_products()
        self.__validate_results()
        self.__validate_steps()
        self.__validate_paths()

    def __populate_test_monitor_data(self, workspaces: List[str]):
        self.__create_products(workspaces[0])
        self.__create_results_with_steps(workspaces)
        # paths are automatically populated, there is not a write api

    def __create_products(self, workspace: str):
        products = []
        for part in self.parts:
            products.append({
                'name': f'{part} Name',
                'partNumber': part,
                'family': f'{part}-family',
                'keywords': [f'{part}-keyword-1', f'{part}-keyword-2'],
                'properties': {f'{part}Property': f'{part}Value', 'forTest': 'True'},
                'fileIds': [self.__upload_file(workspace)]
            })

        response = self.post(PRODUCTS_ROUTE, json={'products': products})
        response.raise_for_status()

    def __create_results_with_steps(self, workspaces: List[str]):
        for workspace in workspaces:
            for i in range(10):
                result_id = self.__create_result(workspace, i)
                self.__create_steps(result_id)

    def __create_result(self, workspace: str, index: int):
        programs = ['Program1', 'Program2', 'Program3']
        systems = ['Tester1', 'Tester2', 'Tester3']
        hosts = ['Host1', 'Host2', 'Host3']
        operators = ['Operator1', 'Operator2', 'Operator3']
        keywords = ['keyword1', 'keyword2', 'keyword2', 'keyword4']
        propertyKeys = ['property1', 'property2', 'property3']
        propertyValues = ['value1', 'value2', 'value3']

        fileId = self.__upload_file(workspace)
        result = {
            'programName': self.__select_item(programs, index),
            'status': self.__select_item(self.statuses, index),
            'systemId': self.__select_item(systems, index),
            'hostName': self.__select_item(hosts, index),
            'properties': {
                self.__select_item(propertyKeys, index): self.__select_item(propertyValues, index),
                'forTest': 'True'
            },
            'keywords': [self.__select_item(keywords, index), self.__select_item(keywords, index+1)],
            'serialNumber': str(111111 * index),
            'operator': self.__select_item(operators, index),
            'partNumber': self.__select_item(self.parts, index),
            'fileIds': [fileId],
            'startedAt': self.__select_date(),
            'totalTimeInSeconds': self.__select_item(self.times, index),
            'workspace': workspace
        }

        response = self.post(RESULTS_ROUTE, json={'results': [result]})
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
        response.raise_for_status()

    def __create_step(self, result_id: str, name: str, index: int) -> Dict[str, Any]:
        return {
            'name': f'{name}{index}',
            'resultId': result_id,
            'stepType': 'forTest',
            'status': self.__select_item(self.statuses, index),
            'startedAt': self.__select_date(),
            'totalTimeInSeconds': self.__select_item(self.times, index),
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

    def __select_date(self):
        if not self.__datetime_base:
            delta = timedelta(days=1)
            self.__datetime_base = datetime.now() - delta
        self.__datetime_base += timedelta(seconds=120)
        return self.datetime_to_string(self.__datetime_base)

    def __select_item(self, items: list, index: int):
        return items[index % len(items)]

    def __upload_file(self, workspace: str) -> str:
        response = self.__file_utilities.upload_file(
                self,
                workspace,
                TDMS_PATH)
        uri = response['uri']
        id = urlparse(uri).path.split('/').pop()
        return id

    def __validate_products(self):
        actual_products = self.__get_product_data()
        expected_products = self.read_recorded_data(CATEGORY, 'products', POPULATED_SERVER_RECORD_TYPE)

        if self._relax_validation:
            actual_products = self.__items_with_test_only_property(actual_products)
            expected_products = self.__items_with_test_only_property(expected_products)

        assert expected_products == actual_products

    def __validate_results(self):
        actual_results = self.__get_result_data()
        expected_results = self.read_recorded_data(CATEGORY, 'results', POPULATED_SERVER_RECORD_TYPE)

        if self._relax_validation:
            actual_results = self.__items_with_test_only_property(actual_results)
            expected_results = self.__items_with_test_only_property(expected_results)

        assert expected_results == actual_results

    def __validate_steps(self):
        actual_steps = self.__get_step_data()
        expected_steps = self.read_recorded_data(CATEGORY, 'steps', POPULATED_SERVER_RECORD_TYPE)

        if self._relax_validation:
            actual_steps = self.__steps_for_test_only(actual_steps)
            expected_steps = self.__steps_for_test_only(expected_steps)

        assert expected_steps == actual_steps

    def __validate_paths(self):
        if self._relax_validation:
            print('Skipping paths for relaxed validation')
            return

        actual_paths = self.__get_path_data()
        expected_paths = self.read_recorded_data(CATEGORY, 'paths', POPULATED_SERVER_RECORD_TYPE)

        assert expected_paths == actual_paths

    def __items_with_test_only_property(self, items):
        return [item for item in items if item.get('properties', {}).get('forTest', False)]

    def __steps_for_test_only(self, steps):
        return [step for step in steps if step.get('stepType', '') == 'forTest']

    def __record_data(self, record_type: str):
        self.__record_product_data(record_type)
        self.__record_result_data(record_type)
        self.__record_step_data(record_type)
        self.__record_path_data(record_type)

    def __record_product_data(self, record_type: str):
        products = self.__get_product_data()
        self.record_data(CATEGORY, 'products', record_type, products)

    def __record_result_data(self, record_type: str):
        results = self.__get_result_data()
        self.record_data(CATEGORY, 'results', record_type, results)

    def __record_step_data(self, record_type: str):
        steps = self.__get_step_data()
        self.record_data(CATEGORY, 'steps', record_type, steps)

    def __record_path_data(self, record_type: str):
        paths = self.__get_path_data()
        self.record_data(CATEGORY, 'paths', record_type, paths)

    def __get_product_data(self):
        return self.get_all_with_continuation_token(PRODUCTS_ROUTE, 'products')

    def __get_result_data(self):
        return self.get_all_with_continuation_token(RESULTS_ROUTE, 'results')

    def __get_step_data(self):
        return self.get_all_with_continuation_token(STEPS_ROUTE, 'steps')

    def __get_path_data(self):
        return self.get_all_with_continuation_token(PATHS_ROUTE, 'paths')


if __name__ == '__main__':
    handle_command_line(TestTestMonitor)
