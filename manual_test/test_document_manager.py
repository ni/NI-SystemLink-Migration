import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from requests.models import Response
from manual_test.manual_test_base import \
    ManualTestBase, \
    handle_command_line, \
    CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
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


class TestDocumentManager(ManualTestBase):

    def populate_data(self) -> None:
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace_for_test(self)
        for workspace_id in workspace_utilities.get_workspaces(self):
            self.__populate_test_dashboard(workspace_id)

        self.__record_all_web_apps(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self) -> None:
        self.__record_all_web_apps(CLEAN_SERVER_RECORD_TYPE)

    def validate_data(self) -> None:
        pass

    def __record_all_web_apps(self, record_type: str):
        all_apps = self.__get_all_web_apps()
        self.record_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            all_apps)
        self.record_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_CONTENT_COLLECTION_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            self.__get_all_content_by_app(all_apps))

    def __get_all_web_apps(self) -> List[Dict[str, Any]]:
        return self.get_all_with_continuation_token(GET_APPS_ROUTE, 'webapps')

    def __get_app_content(self, app: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        uri = GET_APP_CONTENT_ROUTE_FORMAT.format(app_id=app['id'])
        response = self.get(uri)
        if response.status_code != 200:
            # Apps can have no content. Don't fail on error.
            return None

        return response.json()

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
        dashboard = self.__create_test_dashboard(workspace_id)
        self.__add_content_to_dashboard(dashboard)

    def __create_test_dashboard(self, workspace_id: str) -> Dict[str, Any]:
        new_dashboard = {
            'name': 'Test Dashboard',
            'policyIds': [],
            'properties':  {'forTest': 'True'},
            'shared': 'private',
            'type': 'TileDashboard',
            'workspace': workspace_id
        }
        response = self.post(CREATE_APP_ROUTE, json=new_dashboard)
        response.raise_for_status()

        return response.json()

    def __add_content_to_dashboard(self, dashboard: Dict[str, Any]):
        # uri = ADD_APP_CONTENT_ROUTE_FORMAT.format(app_id=dashboard['id'])
        # with open(DASHBOARD_CONTENT_FILE_PATH, 'rb') as file:
        #     response = self.put(uri, files={'filename': file})
        #     print(response.content)
        #     response.raise_for_status()
        pass


if __name__ == '__main__':
    handle_command_line(TestDocumentManager)
