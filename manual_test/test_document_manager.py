import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from manual_test.manual_test_base import \
    ManualTestBase, \
    handle_command_line, \
    CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'DocumentManager'
DOCUMENT_MANAGER_DATABASE_NAME = 'nidashboardbuilder'
TEST_NAME = 'DocumentManagerMigrationTest'
GET_APPS_ROUTE = 'niapp/v1/webapps'
CREATE_APP_ROUTE = 'niapp/v1/webapps'
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

        self.record_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            self.__get_all_web_apps())

    def record_initial_data(self) -> None:
        self.record_json_data(
            SERVICE_NAME,
            DOCUMENT_MANAGER_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            self.__get_all_web_apps())

    def validate_data(self) -> None:
        pass

    def __get_all_web_apps(self) -> List[Dict[str, Any]]:
        return self.get_all_with_continuation_token(GET_APPS_ROUTE, 'webapps')

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
