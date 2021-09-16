import base64
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from manual_test.utilities.notification_utilities import NotificationUtilities
from manual_test.manual_test_base import (
    ManualTestBase,
    handle_command_line,
    CLEAN_SERVER_RECORD_TYPE,
    POPULATED_SERVER_RECORD_TYPE
)
import time
from typing import Any, Dict, List

SERVICE_NAME = 'PackageRepository'
TEST_NAME = f'{SERVICE_NAME}MigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
GET_FEEDS_ROUTE = 'nirepo/v1/feeds?omitPackageReferences=false'
CREATE_FEEDS_ROUTE = 'nirepo/v1/feeds'
GET_PACKAGES_ROUTE = 'nirepo/v1/packages?omitAttributes=false&omitFeedReferences=false'
GET_JOBS_ROUTE = 'nirepo/v1/jobs'
GET_JOB_ROUTE_FORMAT = 'nirepo/v1/jobs?id={job_id}'
GET_STORE_ITEMS_ROUTE_FORMAT = 'nirepo/v1/store/items?pageSize={page_size}&pageNumber={page_number}'

# 10s wait time
WAIT_INCREMENT_SECONDS = 0.1
MAX_WAIT_ITERATIONS = 100


class TestRepository(ManualTestBase):
    def populate_data(self):
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace(TEST_WORKSPACE_NAME, self)
        for workspace in workspace_utilities.get_workspaces(self):
            feed_id = self.__create_feed(workspace)

        self.__record_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self):
        self.__record_data(CLEAN_SERVER_RECORD_TYPE)

    def validate_data(self):
        pass

    def __record_data(self, record_type: str):
        feeds = self.__get_feeds()
        self.record_json_data(
            SERVICE_NAME,
            'feeds',
            record_type,
            feeds)
        self.__save_packages_files(record_type, feeds)
        self.record_json_data(
            SERVICE_NAME,
            'packages',
            record_type,
            self.__get_packages())
        self.record_json_data(
            SERVICE_NAME,
            'jobs',
            record_type,
            self.__get_jobs())
        # We don't control the store, but query a subset of items to verify
        # the service is configured correctly.
        self.record_json_data(
            SERVICE_NAME,
            'store',
            record_type,
            self.__get_store_items(100))

    def __save_packages_files(self, record_type: str, feeds: Dict[str, Any]):
        for feed in feeds['feeds']:
            contents = self.__read_packages_file_contents(feed)
            feed_id = feed['id']
            self.record_text(
                SERVICE_NAME,
                f'Packages_{feed_id}',
                record_type,
                contents)

    def __read_packages_file_contents(self, feed: Dict[str, Any]) -> str:
        uri = feed['directoryUri'] + '/Packages'
        response = self.get(uri, auth=None) # Disable auth for this route
        response.raise_for_status()

        return response.content.decode('utf-8')

    def __get_feeds(self) -> List[Dict[str, Any]]:
        response = self.get(GET_FEEDS_ROUTE)
        response.raise_for_status()
        return response.json()

    def __get_packages(self) -> List[Dict[str, Any]]:
        response = self.get(GET_PACKAGES_ROUTE)
        response.raise_for_status()
        return response.json()

    def __get_jobs(self) -> List[Dict[str, Any]]:
        response = self.get(GET_JOBS_ROUTE)
        response.raise_for_status()
        return response.json()

    def __get_job(self, job_id: str) -> Dict[str, Any]:
        uri = GET_JOB_ROUTE_FORMAT.format(job_id=job_id)
        response = self.get(uri)
        response.raise_for_status()
        return response.json()['jobs'][0]

    def __get_store_items(self, page_size: int, page_number: int = 0) -> List[Dict[str, Any]]:
        uri = GET_STORE_ITEMS_ROUTE_FORMAT.format(page_size=page_size, page_number=page_number)
        response = self.get(uri)
        response.raise_for_status()
        return response.json()

    def __create_feed(self, workspace_id: str) -> str:
        feed = {
            'feedName': f'{TEST_NAME}-test-feed',
            'name': f'Feed for {TEST_NAME}',
            'description': f'Test feed created for {TEST_NAME}',
            'platform': f'windows',
            'workspace': workspace_id
        }
        response = self.post(
            CREATE_FEEDS_ROUTE,
            retries=self.build_default_400_retry(),
            json=feed
        )
        response.raise_for_status()

        job_id = response.json()['jobId']
        feed_id = self.__wait_until_job_completed(job_id)
        return feed_id

    def __wait_until_job_completed(self, job_id: str) -> str:
        job = None
        complete = False
        iteration = 0
        while not complete:
            time.sleep(WAIT_INCREMENT_SECONDS)

            job = self.__get_job(job_id)
            status = job['status']

            if status == 'FAILED':
                raise RuntimeError(f'Job {job_id} failed!')
            complete = job['status'] == 'SUCCEEDED'

            if not complete and iteration >= MAX_WAIT_ITERATIONS:
                raise TimeoutError(f'Job {job_id} did not complete in 10 seconds.')
            iteration = iteration + 1

        return job['resourceId']


if __name__ == '__main__':
    handle_command_line(TestRepository)

