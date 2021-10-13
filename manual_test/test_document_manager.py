import base64
from pathlib import Path
from typing import Any, Dict, List, Optional

from manual_test.manual_test_base import \
    ManualTestBase, \
    handle_command_line, \
    CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.user_utilities import UserUtilities
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'DocumentManager'
DOCUMENT_MANAGER_DATABASE_NAME = 'nidashboardbuilder'
DOCUMENT_MANAGER_CONTENT_COLLECTION_NAME = 'content'
TEST_NAME = 'DocumentManagerMigrationTest'
GET_APPS_ROUTE = 'niapp/v1/webapps'
CREATE_APP_ROUTE = 'niapp/v1/webapps'
GET_APP_CONTENT_ROUTE_FORMAT = 'niapp/v1/webapps/{app_id}/content'
ADD_APP_CONTENT_ROUTE_FORMAT = 'niapp/v1/webapps/{app_id}/content'

# File content used to populate data
ASSETS_PATH = Path(__file__).parent / 'assets'
DASHBOARD_CONTENT_FILE_NAME = 'sample_dashboard_content.json'
DASHBOARD_CONTENT_FILE_PATH = ASSETS_PATH / DASHBOARD_CONTENT_FILE_NAME
WEBVI_CONTENT_FILE_NAME = 'helloweb_1.0.0.0_windows_x64.nipkg'
WEBVI_CONTENT_FILE_PATH = ASSETS_PATH / WEBVI_CONTENT_FILE_NAME


class TestDocumentManager(ManualTestBase):

    def populate_data(self) -> None:
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace_for_test(self)
        for workspace_id in workspace_utilities.get_workspaces(self):
            self.__populate_test_dashboard(workspace_id)
            self.__populate_test_webvi(workspace_id)

        self.__record_all_web_apps(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self) -> None:
        self.__record_all_web_apps(CLEAN_SERVER_RECORD_TYPE)

    def validate_data(self) -> None:
        source_app_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        source_content_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_CONTENT_COLLECTION_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_app_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_app_snapshot = self.__get_all_web_apps()
        current_content_snapshot = self.__get_all_content_by_app(current_app_snapshot)

        current_workspace_ids = WorkspaceUtilities().get_workspaces(self)
        current_users = UserUtilities().get_all_users(self)

        test_app_count = 0
        for app in current_app_snapshot:
            if self.__is_test_app(app):
                expected_app = self.find_record_with_matching_id(app, source_app_snapshot)
                assert expected_app == app
                self.__assert_has_valid_links(app, current_workspace_ids, current_users)
                self.__assert_has_expected_content(
                    app,
                    source_content_snapshot,
                    current_content_snapshot)
                test_app_count = test_app_count + 1
            else:
                # Built-in dashboards may vary by version. Just make sure the item
                # comes from somewhere.
                source_app = self.__find_by_name(app, source_app_snapshot)
                target_app = self.__find_by_name(app, target_app_snapshot)
                assert source_app is not None or target_app is not None

        assert test_app_count > 0

    def __record_all_web_apps(self, record_type: str):
        all_apps = self.__get_all_web_apps()
        self.record_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_DATABASE_NAME,
            record_type,
            all_apps)
        self.record_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_CONTENT_COLLECTION_NAME,
            record_type,
            self.__get_all_content_by_app(all_apps))

    def __get_all_web_apps(self) -> List[Dict[str, Any]]:
        return self.get_all_with_continuation_token(GET_APPS_ROUTE, 'webapps')

    def __get_app_content(self, app: Dict[str, Any]) -> Optional[str]:
        uri = GET_APP_CONTENT_ROUTE_FORMAT.format(app_id=app['id'])
        response = self.get(uri)
        if response.status_code != 200:
            # Apps can have no content. Don't fail on error.
            return None

        return str(base64.b64encode(response.content))

    def __get_all_content_by_app(self, apps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_content = []
        for app in apps:
            content = self.__get_app_content(app)
            if content is not None:
                all_content.append({
                    'appId': app['id'],
                    'content': content
                })

        return all_content

    def __populate_test_dashboard(self, workspace_id: str):
        dashboard = self.__create_test_app('Test Dashboard', 'TileDashboard', workspace_id)
        self.__add_content_to_app(dashboard, DASHBOARD_CONTENT_FILE_PATH)

    def __populate_test_webvi(self, workspace_id):
        webvi = self.__create_test_app('Test WebVI', 'WebVI', workspace_id)
        self.__add_content_to_app(webvi, WEBVI_CONTENT_FILE_PATH)

    def __create_test_app(self, name: str, type: str,  workspace_id: str) -> Dict[str, Any]:
        new_dashboard = {
            'name': name,
            'policyIds': [],
            'properties':  {'forTest': 'True'},
            'shared': 'private',
            'type': type,
            'workspace': workspace_id
        }
        response = self.post(CREATE_APP_ROUTE, json=new_dashboard)
        response.raise_for_status()

        return response.json()

    def __add_content_to_app(self, dashboard: Dict[str, Any], content_path: Path):
        uri = ADD_APP_CONTENT_ROUTE_FORMAT.format(app_id=dashboard['id'])
        with open(content_path, 'rb') as file:
            response = self.put(uri, data=file)
            response.raise_for_status()

    def __assert_has_valid_links(
        self,
        app: Dict[str, Any],
        current_workspace_ids: List[str],
        current_users: List[Dict[str, Any]]
    ):
        # Workspace may be empty if the dashboard is not workspace-restricted
        workspace_id = app['workspace']
        if workspace_id != '':
            assert workspace_id in current_workspace_ids

        user = self.find_record_by_id(app['userId'], current_users)
        assert user is not None

    def __assert_has_expected_content(
        self,
        app: Dict[str, Any],
        source_content_snapshot: List[Dict[str, Any]],
        current_content_snapshot: List[Dict[str, Any]]
    ):
        expected_content = self.find_record_by_property_value(
            app['id'],
            source_content_snapshot,
            'appId')
        actual_content = self.find_record_by_property_value(
            app['id'],
            current_content_snapshot,
            'appId')
        assert expected_content == actual_content

    def __is_test_app(self, app: Dict[str, Any]) -> bool:
        return 'forTest' in app['properties']

    def __find_by_name(
        self,
        app: Dict[str, Any],
        collection: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return self.find_record_with_matching_property_value(app, collection, 'name')


if __name__ == '__main__':
    handle_command_line(TestDocumentManager)
