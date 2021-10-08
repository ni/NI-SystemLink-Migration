from datetime import datetime, timedelta
from uuid import uuid4

from manual_test.manual_test_base import ManualTestBase, POPULATED_SERVER_RECORD_TYPE, handle_command_line
# from manual_test.utilities import file_utilities
from manual_test.utilities.file_utilities import FileUtilities
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

ASSETS_ROUTE = '/niapm/v1/assets'
QUERY_ASSETS_ROUTE = '/niapm/v1/query-assets'
ASSOCIATE_FILES_ROUTE_FORMAT = '/niapm/v1/assets/{asset_id}/file'
START_UTILIZATION_ROUTE = '/niapm/v1/assets/start-utilization'
END_UTILIZATION_ROUTE = '/niapm/v1/assets/end-utilization'
UTILIZATION_HEARTBEAT_ROUTE = '/niapm/v1/assets/utilization-heartbeat'
QUERY_ASSET_UTILIZIATION_HISTORY_ROUTE = '/niapm/v1/query-asset-utilization-history'
GET_ASSET_AVAILABILITY_HISTORY_ROUTE_FORMAT = '/niapm/v1/assets/{asset_id}/history/availability'
GET_ASSET_CALIBRATION_HISTORY_ROUTE_FORMAT = '/niapm/v1/assets/{asset_id}/history/calibration'
UPDATE_ASSETS_ROUTE = 'niapm/v1/update-assets'
GET_ASSET_POLICY_ROUTE = '/niapm/v1/policy'
PATCH_ASSET_POLICY_ROUTE = '/niapm/v1/policy'

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
        self.__validate_asset_files()
        self.__validate_utilization()
        self.__validate_availability_histories()
        self.__validate_calibration_histories()
        self.__validate_policy()

    def __populate_asset_data(self, workspaces):
        now = datetime.now()
        (systems, devices) = self.__populate_assets(workspaces)
        self.__populate_asset_files(systems)
        self.__populate_utilization(systems, now)
        self.__populate_availability_histories(devices)
        self.__populate_calibration_histories(devices, now)
        self.__modify_policy()

    def __populate_assets(self, workspaces):
        systems = []
        devices = []
        for workspace_id in workspaces:
            workspace_systems = self.__ensure_system_asset_exists(workspace_id)
            workspace_devices = self.__ensure_device_asset_exists(workspace_id, workspace_systems)
            systems.extend(workspace_systems)
            devices.extend(workspace_devices)
        return (systems, devices)

    def __populate_asset_files(self, systems):
        # TODO: AB#1667286 Asset files are bugged. Disabling validation until that is fixed.
        # file_utilities = FileUtilities()
        # for system in systems:
        #     if len(system['fileIds']) < 1:
        #         file_id = self.__upload_file_for_system(system, file_utilities)
        #         self.__associate_file(file_id, system)
        pass

    # def __upload_file_for_system(self, system, file_utilities: FileUtilities):
    #     system_name = system['name']
    #     text = f'File for {system_name}'
    #     filename = f'{system_name}.txt'
    #     result = file_utilities.upload_inline_text_file(self, system['workspace'], text, filename)

    #     # Split the returned URI to get the ID
    #     return result['uri'].split('/')[-1]

    # def __associate_file(self, file_id, system):
    #     uri = ASSOCIATE_FILES_ROUTE_FORMAT.format(asset_id=system['id'])
    #     request = {
    #         'fileIds': [file_id]
    #     }
    #     response = self.post(uri, json=request)
    #     response.raise_for_status()

    def __populate_utilization(self, systems, now):
        date = now - timedelta(hours=len(systems))
        delta = timedelta(minutes=7)
        for system in systems:
            identifier = str(uuid4())
            self.__start_asset_utilization(system, date, identifier)
            date += delta
            self.__asset_utilization_heartbeat(date, identifier)
            date += delta
            self.__end_asset_utilization(date, identifier)
            date += delta

    def __populate_calibration_histories(self, devices, now):
        calibration_date = now - timedelta(weeks=8)
        external_calibration = {
            'temperatureSensors': [{
                'name': 'Test Sensor',
                'reading': 48
            }],
            'isLimited': False,
            'date': self.datetime_to_string(calibration_date),
            'recommendedInterval': 12,
            'nextRecommendedDate': self.datetime_to_string(calibration_date + timedelta(weeks=48)),
            'comments': 'Fake calibration for test',
            'entryType': 'MANUAL',
            'operator': {
                'displayName': 'Test Operator'
            }
        }
        updates = []
        for device in devices:
            update = {
                'id': device['id'],
                'externalCalibration': external_calibration
            }
            updates.append(update)
        self.__update_assets(updates)

        calibration_date = now - timedelta(days=7)
        self_calibration = {
            'temperatureSensors': [{
                'name': 'Test Sensor',
                'reading': 44
            }],
            'isLimited': False,
            'date': self.datetime_to_string(calibration_date)
        }
        updates = []
        for device in devices:
            update = {
                'id': device['id'],
                'selfCalibration': self_calibration
            }
            updates.append(update)
        self.__update_assets(updates)

    def __update_assets(self, updates):
        response = self.post(UPDATE_ASSETS_ROUTE, json={'assets': updates})
        response.raise_for_status()
        return response.json()

    def __populate_availability_histories(self, devices):
        # TEST GAP: Currently, availability histories are only tracked for assets
        # that are present in a connected system. For now, we are not actually
        # populating this database, although we still store and validate the contents.
        pass

    def __modify_policy(self):
        policy = {
            'calibrationPolicy': {
                'daysForApproachingCalibrationDueDate': 123
            },
            'workingHoursPolicy': {
                'startTime': '12:00:00',
                'endTime': '16:00:00'
            }
        }
        self.patch(PATCH_ASSET_POLICY_ROUTE, json=policy)

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
                'name': 'Test System',
                'modelName': 'Test System Model',
                'modelNumber': 123,
                'serialNumber': f'{uuid4()}',
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
                'name': 'Test Device',
                'modelName': 'Test Device Model',
                'modelNumber': 321,
                'serialNumber': f'{uuid4()}',
                'vendorName': 'Test Device Vendor',
                'vendorNumber': 654,
                'assetType': 'GENERIC',
                'busType': 'PCI_PXI',
                'supportsSelfCalibration': True,
                'supportsExternalCalibration': True,
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
        self.__record_asset_files(record_type)
        self.__record_utilization_data(record_type)
        self.__record_availibility_histories(record_type)
        self.__record_calibration_histories(record_type)
        self.__record_policy(record_type)

    def __record_asset_data(self, record_type):
        assets = self.__get_assets()
        self.record_json_data(CATEGORY, 'assets', record_type, assets)

    def __record_asset_files(self, record_type):
        files = self.__get_asset_files()
        self.record_json_data(CATEGORY, 'files', record_type, files)

    def __record_utilization_data(self, record_type):
        utilization = self.__get_utilization()
        self.record_json_data(CATEGORY, 'utilization', record_type, utilization)

    def __record_availibility_histories(self, record_type):
        availability_histories = self.__get_availability_histories_by_asset()
        self.record_json_data(CATEGORY, 'availibility_histories', record_type, availability_histories)

    def __record_calibration_histories(self, record_type):
        calibration_histories = self.__get_calibration_histories_by_asset()
        self.record_json_data(CATEGORY, 'calibration_histories', record_type, calibration_histories)

    def __record_policy(self, record_type):
        policy = self.__get_policy()
        self.record_json_data(CATEGORY, 'policy', record_type, policy)

    def __get_assets(self):
        assets = self.get_all_with_skip_take(ASSETS_ROUTE, 'assets')
        return assets

    def __get_asset_files(self):
        files = []
        file_utilities = FileUtilities()
        for asset in self.__get_assets():
            for file_id in asset['fileIds']:
                files.append(file_utilities.get_file(self, file_id))

        return files

    def __get_utilization(self):
        utilization = self.query_all_with_continuation_token(
            QUERY_ASSET_UTILIZIATION_HISTORY_ROUTE, {}, 'assetUtilizations')
        return utilization

    def __get_availability_histories_by_asset(self):
        histories_by_asset = []
        for asset in self.__get_assets():
            history = self.__get_availability_history(asset)
            histories_by_asset.append({
                'id': asset['id'],
                'history': history
            })

        return histories_by_asset

    def __get_availability_history(self, asset):
        # Query into the future to avoid potential precision issues.
        uri = GET_ASSET_AVAILABILITY_HISTORY_ROUTE_FORMAT.format(asset_id=asset['id'])
        end_date = self.datetime_to_string(datetime.now() + timedelta(hours=12))
        arguments = f'?startDate=1900-01-01T00:00:00.000Z&endDate={end_date}&granularity=NONE'
        uri = uri + arguments
        response = self.get(uri)
        response.raise_for_status()
        return response.json()

    def __get_calibration_histories_by_asset(self):
        histories_by_asset = []
        for asset in self.__get_assets():
            history = self.__get_calibration_history(asset)
            histories_by_asset.append({
                'id': asset['id'],
                'history': history
            })

        return histories_by_asset

    def __get_calibration_history(self, asset):
        uri = GET_ASSET_CALIBRATION_HISTORY_ROUTE_FORMAT.format(
            asset_id=asset['id']
        )
        history = self.get_all_with_skip_take(uri, 'calibrationHistory')
        return history

    def __get_policy(self):
        response = self.get(GET_ASSET_POLICY_ROUTE)
        response.raise_for_status()
        return response.json()

    def __validate_assets(self):
        actual_assets = self.__get_assets()
        expected_assets = self.read_recorded_json_data(CATEGORY, 'assets', POPULATED_SERVER_RECORD_TYPE)

        assert len(actual_assets) == len(expected_assets)
        for actual_asset in actual_assets:
            expected_asset = self.find_record_by_id(actual_asset['id'], expected_assets)
            assert actual_asset == expected_asset

    def __validate_asset_files(self):
        # TODO: AB#1667286 Asset files are bugged. Disabling validation until that is fixed.
        # actual_assets = self.__get_asset_files()
        # expected_assets = self.read_recorded_json_data(CATEGORY, 'files', POPULATED_SERVER_RECORD_TYPE)
        # assert actual_assets == expected_assets
        pass

    def __validate_utilization(self):
        actual_utilizations = self.__get_utilization()
        expected_utilizations = self.read_recorded_json_data(CATEGORY, 'utilization', POPULATED_SERVER_RECORD_TYPE)

        assert len(actual_utilizations) == len(expected_utilizations)
        for actual_utilization in actual_utilizations:
            expected_utilization = self.find_record_by_property_value(
                actual_utilization['utilizationIdentifier'],
                expected_utilizations,
                'utilizationIdentifier')
            assert actual_utilization == expected_utilization

    def __validate_availability_histories(self):
        actual_histories = self.__get_availability_histories_by_asset()
        expected_histories = self.read_recorded_json_data(
            CATEGORY,
            'availibility_histories',
            POPULATED_SERVER_RECORD_TYPE
        )

        assert len(actual_histories) == len(expected_histories)
        for actual_history in actual_histories:
            expected_history = self.find_record_by_id(actual_history['id'], expected_histories)
            assert actual_history == expected_history

    def __validate_calibration_histories(self):
        actual_histories = self.__get_calibration_histories_by_asset()
        expected_histories = self.read_recorded_json_data(
            CATEGORY,
            'calibration_histories',
            POPULATED_SERVER_RECORD_TYPE
        )

        assert len(actual_histories) == len(expected_histories)
        for actual_history in actual_histories:
            expected_history = self.find_record_by_id(actual_history['id'], expected_histories)
            assert actual_history == expected_history

    def __validate_policy(self):
        actual_policy = self.__get_policy()
        expected_policy = self.read_recorded_json_data(CATEGORY, 'policy', POPULATED_SERVER_RECORD_TYPE)
        assert actual_policy == expected_policy


if __name__ == '__main__':
    handle_command_line(TestAsset)
