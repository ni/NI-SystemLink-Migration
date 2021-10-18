from pathlib import Path
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
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
TEST_FEED_NAME = f'{TEST_NAME}-test-feed'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
GET_FEEDS_ROUTE = 'nirepo/v1/feeds?omitPackageReferences=false'
CREATE_FEEDS_ROUTE = 'nirepo/v1/feeds'
ADD_PACKAGE_REFERENCE_ROUTE_FORMAT = 'nirepo/v1/feeds/{feed_id}/add-package-references'
GET_PACKAGES_ROUTE = 'nirepo/v1/packages?omitAttributes=false&omitFeedReferences=false'
UPLOAD_PACKAGES_ROUTE = 'nirepo/v1/upload-packages?shouldOverwrite=true'
GET_JOBS_ROUTE = 'nirepo/v1/jobs'
GET_JOB_ROUTE_FORMAT = 'nirepo/v1/jobs?id={job_id}'
GET_STORE_ITEMS_ROUTE_FORMAT = 'nirepo/v1/store/items?pageSize={page_size}&pageNumber={page_number}'

# Package to add to our test feed
ASSETS_PATH = Path(__file__).parent / 'assets'
TEST_PACKAGE_NAME = 'test-package'
TEST_PACKAGE_FILE_NAME = f'{TEST_PACKAGE_NAME}_1.0.0-0_x64.ipk'
TEST_PACKAGE_PATH = ASSETS_PATH / TEST_PACKAGE_FILE_NAME

# 10s wait time
WAIT_INCREMENT_SECONDS = 0.1
MAX_WAIT_ITERATIONS = 100


class TestRepository(ManualTestBase):
    def populate_data(self):
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace_for_test(self)
        feed_ids = []
        for workspace in workspace_utilities.get_workspaces(self):
            feed_ids.append(self.__create_feed(workspace))

        package_id = self.__upload_package(TEST_PACKAGE_PATH)

        for feed_id in feed_ids:
            self.__add_package_reference(feed_id, package_id)

        self.__record_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self):
        self.__record_data(CLEAN_SERVER_RECORD_TYPE)

    def validate_data(self):
        current_feeds = self.__get_feeds()
        current_packages = self.__get_packages()
        workspaces = WorkspaceUtilities().get_workspaces(self)
        self.__validate_feeds(current_feeds, current_packages, workspaces)
        self.__validate_packages(current_feeds, current_packages)
        self.__validate_jobs()
        self.__validate_store_items()

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

    def __save_packages_files(self, record_type: str, feeds: List[Dict[str, Any]]):
        for feed in feeds:
            contents = self.__download_packages_file_contents(feed)
            feed_id = feed['id']
            self.record_text(
                SERVICE_NAME,
                self.__build_packages_file_record_name(feed_id),
                record_type,
                contents)

    def __read_packages_file_record(
        self,
        record_type: str,
        feed: Dict[str, Any],
        required: bool = True
    ) -> str:
        feed_id = feed['id']
        return self.read_recorded_text(
            SERVICE_NAME,
            self.__build_packages_file_record_name(feed_id),
            record_type,
            required
        )

    def __build_packages_file_record_name(self, feed_id: str) -> str:
        return f'Packages_{feed_id}'

    def __download_packages_file_contents(self, feed: Dict[str, Any]) -> str:
        uri = feed['directoryUri'] + '/Packages'
        content = self.__download_file_from_feed(uri)
        return content.decode('utf-8')

    def __download_file_from_feed(self, uri) -> bytes:
        response = self.get(uri, auth=None)  # Disable auth for this route
        response.raise_for_status()
        return response.content

    def __get_feeds(self) -> List[Dict[str, Any]]:
        response = self.get(GET_FEEDS_ROUTE)
        response.raise_for_status()
        return response.json()['feeds']

    def __get_packages(self) -> List[Dict[str, Any]]:
        response = self.get(GET_PACKAGES_ROUTE)
        response.raise_for_status()
        return response.json()['packages']

    def __get_jobs(self) -> List[Dict[str, Any]]:
        response = self.get(GET_JOBS_ROUTE)
        response.raise_for_status()
        return response.json()['jobs']

    def __get_job(self, job_id: str) -> Dict[str, Any]:
        uri = GET_JOB_ROUTE_FORMAT.format(job_id=job_id)
        response = self.get(uri)
        response.raise_for_status()
        return response.json()['jobs'][0]

    def __get_store_items(self, page_size: int, page_number: int = 0) -> List[Dict[str, Any]]:
        uri = GET_STORE_ITEMS_ROUTE_FORMAT.format(page_size=page_size, page_number=page_number)
        response = self.get(uri)
        response.raise_for_status()
        return response.json()['items']

    def __create_feed(self, workspace_id: str) -> str:
        feed = {
            'feedName': TEST_FEED_NAME,
            'name': f'Feed for {TEST_NAME}',
            'description': f'Test feed created for {TEST_NAME}',
            'platform': 'ni-linux-rt',
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

    def __upload_package(self, package_path: str) -> str:
        file_spec = {'filename': open(package_path, 'rb')}
        response = self.post(UPLOAD_PACKAGES_ROUTE, files=file_spec)
        response.raise_for_status()

        job_id = response.json()['jobIds'][0]
        package_id = self.__wait_until_job_completed(job_id)
        return package_id

    def __add_package_reference(self, feed_id: str, package_id: str):
        uri = ADD_PACKAGE_REFERENCE_ROUTE_FORMAT.format(feed_id=feed_id)
        references = {
            'packageReferences': [package_id]
        }
        response = self.post(uri, json=references)
        response.raise_for_status()

        job_id = response.json()['jobId']
        self.__wait_until_job_completed(job_id)

    def __wait_until_job_completed(self, job_id: str) -> str:
        job = {}
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

    def __validate_feeds(
        self,
        current_feeds: List[Dict[str, Any]],
        current_packages: List[Dict[str, Any]],
        workspaces: List[str]
    ):
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            'feeds',
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_json_data(
            SERVICE_NAME,
            'feeds',
            CLEAN_SERVER_RECORD_TYPE,
            required=False)

        migrated_record_count = 0
        for feed in current_feeds:
            expected_feed = self.find_record_with_matching_id(feed, source_service_snapshot)
            if expected_feed is not None:
                self.__assert_feeds_equal(expected_feed, feed)
                self.__assert_has_valid_workspace(feed, workspaces)
                self.__assert_has_valid_package_references(feed, current_packages)
                self.__assert_matching_packages_files(feed)
                migrated_record_count = migrated_record_count + 1
            else:
                # This test does not expect any auto-generated feeds. It just verifies that if any extra
                # feeds exist, they were present when the server first started.
                expected_feed = self.__find_feed_by_name(feed, target_service_snaphot)
                assert expected_feed is not None

        assert len(source_service_snapshot) == migrated_record_count

    def __validate_packages(
        self,
        current_feeds: List[Dict[str, Any]],
        current_packages: List[Dict[str, Any]]
    ):
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            'packages',
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_json_data(
            SERVICE_NAME,
            'packages',
            CLEAN_SERVER_RECORD_TYPE,
            required=False)

        migrated_record_count = 0
        found_test_package = False
        for package in current_packages:
            expected_package = self.find_record_with_matching_id(package, source_service_snapshot)
            if expected_package is not None:
                self.__assert_packages_equal(expected_package, package)
                self.__assert_has_valid_feed_references(package, current_feeds)
                if self.__is_test_package(package):
                    self.__assert_can_download_test_package(package)
                    found_test_package = True
                migrated_record_count = migrated_record_count + 1
            else:
                # This test does not expect any auto-generated feeds. It just verifies that if any extra
                # feeds exist, they were present when the server first started.
                expected_package = self.__find_package_by_name_and_version(package, target_service_snaphot)
                assert expected_package is not None

        assert len(source_service_snapshot) == migrated_record_count
        assert found_test_package

    def __validate_jobs(self):
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            'jobs',
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        current_jobs = self.__get_jobs()

        migrated_record_count = 0
        for job in current_jobs:
            expected_job = self.find_record_with_matching_id(job, source_service_snapshot)
            if expected_job is not None:
                self.__assert_jobs_equal(expected_job, job)
                migrated_record_count = migrated_record_count + 1
            else:
                # Not expecting any jobs to be created after restore.
                job_id = job['id']
                print(f'WARNING: Found unexpected job {job_id}')

        assert len(source_service_snapshot) == migrated_record_count

    def __validate_store_items(self):
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            'store',
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        current_store_items = self.__get_store_items(len(source_service_snapshot))

        # ASSUMPTION: The store remains stable for the duration of this test.
        assert source_service_snapshot == current_store_items

    def __assert_feeds_equal(self, expected_feed: Dict[str, Any], actual_feed: Dict[str, Any]):
        assert expected_feed == actual_feed

    def __assert_has_valid_workspace(self, feed: Dict[str, Any], workspaces: List[str]):
        matching_workspace = next((workspace for workspace in workspaces if workspace == feed['workspace']), None)
        assert matching_workspace is not None

    def __assert_has_valid_package_references(self, feed: Dict[str, Any], current_packages: List[Dict[str, Any]]):
        for package_id in feed['packageReferences']:
            matching_package = self.find_record_by_id(package_id, current_packages)
            assert matching_package is not None

    def __assert_matching_packages_files(self, feed: Dict[str, Any]):
        expected_contents = self.__read_packages_file_record(POPULATED_SERVER_RECORD_TYPE, feed)
        actual_contents = self.__download_packages_file_contents(feed)
        # Ignore line ending differences
        assert expected_contents.splitlines() == actual_contents.splitlines()

    def __assert_packages_equal(self, expected_package: Dict[str, Any], actual_package: Dict[str, Any]):
        assert expected_package == actual_package

    def __assert_has_valid_feed_references(
        self,
        package: Dict[str, Any],
        current_feeds: List[Dict[str, Any]]
    ):
        for feed_id in package['feedReferences']:
            matching_feed = self.find_record_by_id(feed_id, current_feeds)
            assert matching_feed is not None

    def __assert_can_download_test_package(self, package: Dict[str, Any]):
        expected_content = self.__read_test_package()
        actual_content = self.__download_file_from_feed(package['fileUri'])
        assert expected_content == actual_content

    def __assert_jobs_equal(self, expected_job: Dict[str, Any], actual_job: Dict[str, Any]):
        assert expected_job == actual_job

    def __read_test_package(self) -> bytes:
        with open(TEST_PACKAGE_PATH, 'rb') as file:
            return file.read()

    def __is_test_package(self, package) -> bool:
        return package['metadata']['packageName'] == TEST_PACKAGE_NAME

    def __find_feed_by_name(self, feed: Dict[str, Any], collection: List[Dict[str, Any]]):
        name = feed['feedName']
        return next((record for record in collection if record['feedName'] == name))

    def __find_package_by_name_and_version(self, package: Dict[str, Any], collection: List[Dict[str, Any]]):
        return next((record for record in collection if self.__has_matching_name_and_version(package, record)))

    def __has_matching_name_and_version(self, package: Dict[str, Any], other_package: Dict[str, Any]) -> bool:
        metadata = package['metadata']
        other_metadata = package['metadata']
        return (metadata['packageName'] == other_metadata['packageName']
                and metadata['version'] == other_metadata['version'])


if __name__ == '__main__':
    handle_command_line(TestRepository)
