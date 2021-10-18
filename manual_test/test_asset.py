from datetime import datetime, timedelta
from uuid import uuid4

from manual_test.manual_test_base import ManualTestBase, POPULATED_SERVER_RECORD_TYPE, handle_command_line
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

ASSETS_ROUTE = '/niapm/v1/assets'
QUERY_ASSETS_ROUTE = '/niapm/v1/query-assets'

START_UTILIZATION_ROUTE = '/niapm/v1/assets/start-utilization'
END_UTILIZATION_ROUTE = '/niapm/v1/assets/end-utilization'
UTILIZATION_HEARTBEAT_ROUTE = '/niapm/v1/assets/utilization-heartbeat'
QUERY_ASSET_UTILIZIATION_HISTORY_ROUTE = '/niapm/v1/query-asset-utilization-history'

CATEGORY = 'assets'


class TestAsset(ManualTestBase):

    def populate_data(self):
        WorkspaceUtilities().create_workspace_for_test(self)
        workspaces = WorkspaceUtilities().get_workspaces(self)
        self.__populate_asset_data(workspaces)
        self.__record_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self):
        """The asset service should not be populated with initial data."""
        pass

    def validate_data(self):
        self.__validate_assets()
        self.__validate_utilization()

    def __populate_asset_data(self, workspaces):
        systems = self.__populate_assets(workspaces)
        self.__populate_utilization(systems)

    def __populate_assets(self, workspaces):
        systems = []
        for workspace_id in workspaces:
            workspace_systems = self.__ensure_system_asset_exists(workspace_id)
            self.__ensure_device_asset_exists(workspace_id, workspace_systems)
            systems.extend(workspace_systems)
        return systems

    def __populate_utilization(self, systems):
        date = datetime.now() - timedelta(hours=len(systems))
        delta = timedelta(minutes=7)
        for system in systems:
            identifier = str(uuid4())
            self.__start_asset_utilization(system, date, identifier)
            date += delta
            self.__asset_utilization_heartbeat(date, identifier)
            date += delta
            self.__end_asset_utilization(date, identifier)
            date += delta

    def __ensure_system_asset_exists(self, workspace_id):
        systems = self.__query_assets(f'Workspace = "{workspace_id}" && AssetType = "SYSTEM"')
        return systems if systems else [self.__create_system_asset(workspace_id)]

    def __ensure_device_asset_exists(self, workspace_id, systems):
        devices = self.__query_assets(f'Workspace = "{workspace_id}" && AssetType != "SYSTEM"')
        return devices if devices else [self.__create_device_asset(workspace_id, systems)]

    def __create_system_asset(self, workspace_id):
        assets = {
            'assets': [{
                'workspace': workspace_id,
                'description': 'Test System',
                'modelName': 'Test System Model',
                'modelNumber': 123,
                'serialNumber': '098765',
                'vendorName': 'Test System Vendor',
                'vendorNumber': 456,
                'assetType': 'SYSTEM',
                'busType': 'BUILT_IN_SYSTEM',
                'location': {
                    'minionId': f'MINION_{uuid4()}'
                }
            }]
        }
        return self.__create_assets(assets)

    def __create_device_asset(self, workspace_id, systems):
        assets = {
            'assets': [{
                'workspace': workspace_id,
                'description': 'Test Device',
                'modelName': 'Test Device Model',
                'modelNumber': 321,
                'serialNumber': '567890',
                'vendorName': 'Test Device Vendor',
                'vendorNumber': 654,
                'assetType': 'GENERIC',
                'busType': 'PCI_PXI',
                'location': {
                    'minionId': systems[0]['location']['minionId']
                }
            }]
        }
        return self.__create_assets(assets)

    def __create_assets(self, assets):
        response = self.post(ASSETS_ROUTE, json=assets)
        response.raise_for_status()
        return response.json()['assets'][0]

    def __start_asset_utilization(self, asset, date, identifier):
        utilization = {
            'utilizationIdentifier': identifier,
            'minionId': asset['location']['minionId'],
            'assetIdentifications': [{
                'modelName': asset['modelName'],
                'modelNumber': asset['modelNumber'],
                'serialNumber': asset['serialNumber'],
                'vendorName': asset['vendorName'],
                'vendorNumber': asset['vendorNumber'],
                'busType': asset['busType']
            }],
            'utilizationCategory': 'migration test category',
            'taskName': 'migration test',
            'userName': 'tester',
            'utilizationTimestamp': self.datetime_to_string(date)
        }
        response = self.post(START_UTILIZATION_ROUTE, json=utilization)
        response.raise_for_status()

    def __end_asset_utilization(self, date, identifier):
        heartbeat = {
            'utilizationIdentifiers': [identifier],
            'utilizationTimestamp': self.datetime_to_string(date)
        }
        response = self.post(END_UTILIZATION_ROUTE, json=heartbeat)
        response.raise_for_status()

    def __asset_utilization_heartbeat(self, date, identifier):
        heartbeat = {
            'utilizationIdentifiers': [identifier],
            'utilizationTimestamp': self.datetime_to_string(date)
        }
        response = self.post(UTILIZATION_HEARTBEAT_ROUTE, json=heartbeat)
        response.raise_for_status()

    def __query_assets(self, filter):
        response = self.post(
            QUERY_ASSETS_ROUTE,
            json={
                'responseFormat': 'JSON',
                'destination': 'INLINE',
                'filter': filter
            })
        response.raise_for_status()
        return response.json()['assets']

    def __record_data(self, record_type):
        self.__record_asset_data(record_type)
        self.__record_utilization_data(record_type)

    def __record_asset_data(self, record_type):
        assets = self.__get_assets()
        self.record_json_data(CATEGORY, 'assets', record_type, assets)

    def __record_utilization_data(self, record_type):
        utilization = self.__get_utilization()
        self.record_json_data(CATEGORY, 'utilization', record_type, utilization)

    def __get_assets(self):
        assets = self.get_all_with_skip_take(ASSETS_ROUTE, 'assets')
        return assets

    def __get_utilization(self):
        utilization = self.query_all_with_continuation_token(
            QUERY_ASSET_UTILIZIATION_HISTORY_ROUTE, {}, 'assetUtilizations')
        return utilization

    def __validate_assets(self):
        actual_assets = self.__get_assets()
        expected_assets = self.read_recorded_json_data(CATEGORY, 'assets', POPULATED_SERVER_RECORD_TYPE)
        assert actual_assets == expected_assets

    def __validate_utilization(self):
        actual_utilization = self.__get_utilization()
        expected_utilization = self.read_recorded_json_data(CATEGORY, 'utilization', POPULATED_SERVER_RECORD_TYPE)
        assert actual_utilization == expected_utilization


if __name__ == '__main__':
    handle_command_line(TestAsset)
