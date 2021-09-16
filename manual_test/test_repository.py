from typing import Any, Dict, List
from manual_test.utilities.notification_utilities import NotificationUtilities
from manual_test.manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE
from manual_test.manual_test_base import POPULATED_SERVER_RECORD_TYPE

SERVICE_NAME = 'PackageRepository'
TEST_NAME = 'AlarmMigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
GET_FEEDS_ROUTE = 'nirepo/v1/feeds?omitPackageReferences=false'
GET_PACKAGES_ROUTE = 'nirepo/v1/packages?omitAttributes=false&omitFeedReferences=false'
GET_STORE_ITEMS_ROUTE_FORMAT = 'nirepo/v1/store/items?pageSize={page_size}&pageNumber={page_number}'


class TestRepository(ManualTestBase):
    def populate_data(self):
        pass

    def record_initial_data(self):
        self.__record_data(CLEAN_SERVER_RECORD_TYPE)

    def validate_data(self):
        pass

    def __record_data(self, record_type: str):
        self.record_data(
            SERVICE_NAME,
            'feeds',
            record_type,
            self.__get_feeds())
        self.record_data(
            SERVICE_NAME,
            'packages',
            record_type,
            self.__get_packages())
        # We don't control the store, but query a subset of items to verify
        # the service is configured correctly.
        self.record_data(
            SERVICE_NAME,
            'store',
            record_type,
            self.__get_store_items(100))

    def __get_feeds(self) -> List[Dict[str, Any]]:
        response = self.get(GET_FEEDS_ROUTE)
        response.raise_for_status()
        return response.json()

    def __get_packages(self) -> List[Dict[str, Any]]:
        response = self.get(GET_PACKAGES_ROUTE)
        response.raise_for_status()
        return response.json()

    def __get_store_items(self, page_size: int, page_number: int = 0) -> List[Dict[str, Any]]:
        uri = GET_STORE_ITEMS_ROUTE_FORMAT.format(page_size=page_size, page_number=page_number)
        response = self.get(uri)
        response.raise_for_status()
        return response.json()


if __name__ == '__main__':
    handle_command_line(TestRepository)

