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
ADD_APP_COUNTENT_ROUTE_FORMAT = 'niapp/v1/webapps/{app_id}/content'


class TestDocumentManager(ManualTestBase):

    def populate_data(self) -> None:
        pass

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


if __name__ == '__main__':
    handle_command_line(TestDocumentManager)
