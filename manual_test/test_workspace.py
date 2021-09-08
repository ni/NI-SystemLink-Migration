from manual_test.manual_test_base import ManualTestBase

AUTH_ROUTE = '/niauth/v1/auth'
WORKSPACES_ROUTE = '/niuser/v1/workspaces'


class TestWorkspace(ManualTestBase):
    def populate_data(self) -> None:
        pass

    def validate_data(self) -> None:
        pass

    def __get_workspaces(self):
        response = self.get(AUTH_ROUTE)
        response.raise_for_status()

        auth = response.json()
        workspaces = [workspace['id'] for workspace in auth['workspaces'] if workspace['enabled']]
        if len(workspaces) < 2:
            raise RuntimeError('User needs access to at least 2 workspaces')

        return workspaces

    def __get_workspace_id(self, workspace_name: str):
        result = self.get(WORKSPACES_ROUTE)
        workspaces = result.json()["workspaces"]
        for workspace in workspaces:
            if workspace["name"] == workspace_name:
                return workspace["id"]
        return None

    def __create_workspace(self, workspace_name: str):
        self.post(WORKSPACES_ROUTE, json={"name": workspace_name})
