from uuid import uuid4

from manual_test.manual_test_base import ManualTestBase, POPULATED_SERVER_RECORD_TYPE, handle_command_line
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

ASSETS_ROUTE = '/niapm/v1/assets'
QUERY_ASSETS_ROUTE = '/niapm/v1/query-assets'

CATEGORY = 'assets'


class TestAsset(ManualTestBase):

    def populate_data(self):
        WorkspaceUtilities().create_workspace_for_test(self)
        workspaces = WorkspaceUtilities().get_workspaces(self)
        self.__populate_asset_data(workspaces)
        self.__record_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self):
        """The file service should not be populated with initial data."""
        pass

    def validate_data(self):
        self.__validate_assets()

    def __populate_asset_data(self, workspaces):
        self.__populate_assets(workspaces)

    def __populate_assets(self, workspaces):
        for workspace_id in workspaces:
            systems = self.__ensure_system_asset_exists(workspace_id)
            self.__ensure_device_asset_exists(workspace_id, systems)

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
                    'minion_id': f'MINION_{uuid4()}'
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
                    'minion_id': systems[0]['location']['minionId']
                }
            }]
        }
        return self.__create_assets(assets)

    def __create_assets(self, assets):
        response = self.post(ASSETS_ROUTE, json=assets)
        response.raise_for_status()
        return response.json()['assets'][0]

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

    def __record_asset_data(self, record_type):
        assets = self.__get_assets()
        self.record_json_data(CATEGORY, 'assets', record_type, assets)

    def __get_assets(self):
        assets = self.get_all_with_skip_take(ASSETS_ROUTE, 'assets')
        assets.sort(key=lambda a : a['id'])
        return assets

    def __validate_assets(self):
        actual_assets = self.__get_assets()
        expected_assets = self.read_recorded_json_data(CATEGORY, 'assets', POPULATED_SERVER_RECORD_TYPE)
        assert actual_assets == expected_assets


if __name__ == '__main__':
    handle_command_line(TestAsset)
