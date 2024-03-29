from manual_test.manual_test_base import ManualTestBase

AUTH_ROUTE = '/niauth/v1/auth'
WORKSPACES_ROUTE = '/niuser/v1/workspaces'
TEST_WORKSPACE_NAME = 'WorkspaceForMigrationTests'


class WorkspaceUtilities:

    @staticmethod
    def get_workspaces(test: ManualTestBase):
        response = test.get(AUTH_ROUTE)
        response.raise_for_status()
        auth = response.json()
        return [workspace['id'] for workspace in auth['workspaces'] if workspace['enabled']]

    @staticmethod
    def get_two_or_more_workspaces(test: ManualTestBase):
        workspaces = WorkspaceUtilities.get_workspaces(test)
        if len(workspaces) < 2:
            raise RuntimeError('User needs access to at least 2 workspaces')
        return workspaces

    @staticmethod
    def get_workspace_id(workspace_name: str, test: ManualTestBase):
        result = test.get(WORKSPACES_ROUTE)
        workspaces = result.json()['workspaces']
        for workspace in workspaces:
            if workspace['name'] == workspace_name:
                return workspace['id']
        return None

    @staticmethod
    def __create_workspace(workspace_name: str, test: ManualTestBase):
        test.post(WORKSPACES_ROUTE, json={'name': workspace_name})

    @staticmethod
    def create_workspace_for_test(test: ManualTestBase):
        WorkspaceUtilities.__create_workspace(TEST_WORKSPACE_NAME, test)
