from manual_test.manual_test_base import \
    ManualTestBase, \
    handle_command_line, \
    CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.user_utilities import UserUtilities
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from typing import Any, Dict, List

SERVICE_NAME = 'Security'
TEST_NAME = 'SecurityMigrationTest'
ROUTE = '/niuser/v1'
USER_ROUTE = ROUTE + '/users'
QUERY_USER_ROUTE = USER_ROUTE + '/query'
AUTH_MAPPING_ROUTE = ROUTE + '/auth-mappings'
AUTH_POLICY_TEMPLATE_ROUTE = '/niauth/v1/policy-templates'
RECORDED_WORKSPACE_DATA_IDENTIFIER = 'workspaces'
RECORDED_USERS_DATA_IDENTIFIER = 'users'
RECORDED_AUTH_MAPPINGS_DATA_IDENTIFIER = 'auth-mappings'


class TestSecurity(ManualTestBase):
    def populate_data(self) -> None:
        self.__populate_server_with_test_data()
        self.__record_security_service_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self) -> None:
        self.__record_security_service_data(CLEAN_SERVER_RECORD_TYPE)

    def validate_data(self) -> None:
        self.__validate_user_migration()
        self.__validate_workspace_migration()
        self.__validate_auth_mapping_migration()

    def __record_security_service_data(self, record_type: str):
        self.__record_workspace_data(record_type)
        self.__record_users_data(record_type)
        self.__record_auth_mapping_data(record_type)

    def __validate_user_migration(self):
        users_source_service_snapshot = self.__read_users_data(POPULATED_SERVER_RECORD_TYPE)
        users_target_service_snapshot = self.__read_users_data(CLEAN_SERVER_RECORD_TYPE)
        users_current_snapshot = self.__get_all_user_data()
        for user in users_current_snapshot:
            expected_user = self.find_record_with_matching_id(user, users_source_service_snapshot)
            if expected_user is not None:
                self.__assert_users_equal(expected_user, user)
            else:
                # Verify items that are generated by the target version and not present in the source.
                expected_user = self.find_record_by_property_value(user, users_target_service_snapshot, 'login')
                assert expected_user is not None
                self.__assert_rules_equal(expected_user, user)

    def __validate_workspace_migration(self):
        workspaces_source_service_snapshot = self.__read_workspace_data(POPULATED_SERVER_RECORD_TYPE)
        workspaces_current_snapshot = self.__get_all_workspaces()
        for source_workspace in workspaces_source_service_snapshot:
            assert source_workspace in workspaces_current_snapshot

    def __validate_auth_mapping_migration(self):
        mappings_source_snapshot = self.__read_auth_mapping_data(POPULATED_SERVER_RECORD_TYPE)
        mappings_target_snapshot = self.__read_auth_mapping_data(CLEAN_SERVER_RECORD_TYPE)
        mappings_current_snapshot = self.__get_all_auth_mappings()
        for mapping in mappings_current_snapshot:
            expected_mapping = self.find_record_with_matching_id(mapping, mappings_source_snapshot)
            if expected_mapping is not None:
                self.__assert_workspaces_equal(expected_mapping, mapping)
            else:
                # Verify items that are generated by the target version and not present in the source.
                expected_mapping = self.find_record_by_property_value(mapping, mappings_target_snapshot, 'name')
                assert expected_mapping is not None
                self.__assert_workspaces_equal(expected_mapping, mapping)

    def __populate_server_with_test_data(self):
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace_for_test(self)
        built_in_policy_template = self.__get_built_in_policy_templates()[0]
        self.__create_test_user(built_in_policy_template['id'])
        for workspace in workspace_utilities.get_two_or_more_workspaces(self):
            self.__create_test_policy_template()
            self.__create_test_auth_mapping(workspace, built_in_policy_template['id'])

    @staticmethod
    def __assert_users_equal(expected_user, user):
        TestSecurity.__assert_dictionaries_equal(expected_user, user, ['updated'])

    @staticmethod
    def __assert_workspaces_equal(expected_workspace, workspace):
        assert expected_workspace == workspace

    def __create_test_auth_mapping(self, workspace_id: str, policy_template_id: str):
        auth_mapping = {
            'type': 'windows-user',
            'policyTemplateId': policy_template_id,
            'workspace': workspace_id,
            'selector': {
                'key': 'user',
                'value': 'test'
            }
        }
        response = self.post(AUTH_MAPPING_ROUTE, json=auth_mapping)
        response.raise_for_status()

    def __create_test_user(self, policy_template_id: str):
        user = {
            'firstName': 'firstname',
            'lastName': 'lastname',
            'email': 'firstname@lastname.net',
            'niuaId': 'niuaId',
            'login': 'firstname',
            'acceptedToS': 'true',
            'policies': [policy_template_id],
            'keywords': ['test-keyword'],
            'properties': {'key': 'value'},
        }
        response = self.post(USER_ROUTE, json=user)
        response.raise_for_status()

    def __create_test_policy_template(self):
        policy_template = {
          'name': 'test-policy-template',
          'type': 'user',
          'statements': [
            {
              'actions': [
                'alarm:Read',
                'alarm:Transition',
                'alarm:AddNote'
              ],
              'resource': [
                '*'
              ],
              'description': 'testdescription'
            }
          ],
        }
        response = self.post(AUTH_POLICY_TEMPLATE_ROUTE, json=policy_template)
        response.raise_for_status()
        return response.json()

    def __record_workspace_data(self, record_type: str):
        self.record_json_data(
            SERVICE_NAME,
            RECORDED_WORKSPACE_DATA_IDENTIFIER,
            record_type,
            self.__get_all_workspaces())

    def __read_workspace_data(self, record_type: str):
        return self.read_recorded_json_data(
            SERVICE_NAME,
            RECORDED_WORKSPACE_DATA_IDENTIFIER,
            record_type)

    def __record_users_data(self, record_type: str):
        self.record_json_data(
            SERVICE_NAME,
            RECORDED_USERS_DATA_IDENTIFIER,
            record_type,
            self.__get_all_user_data())

    def __read_users_data(self, record_type: str):
        return self.read_recorded_json_data(
            SERVICE_NAME,
            RECORDED_USERS_DATA_IDENTIFIER,
            record_type)

    def __record_auth_mapping_data(self, record_type: str):
        self.record_json_data(
            SERVICE_NAME,
            RECORDED_AUTH_MAPPINGS_DATA_IDENTIFIER,
            record_type,
            self.__get_all_auth_mappings())

    def __read_auth_mapping_data(self, record_type: str):
        return self.read_recorded_json_data(
            SERVICE_NAME,
            RECORDED_AUTH_MAPPINGS_DATA_IDENTIFIER,
            record_type)

    def __get_all_workspaces(self) -> List[Dict[str, Any]]:
        workspace_utilities = WorkspaceUtilities()
        return workspace_utilities.get_workspaces(self)

    def __get_all_user_data(self) -> List[Dict[str, Any]]:
        return UserUtilities().get_all_users(self)

    def __get_all_auth_mappings(self):
        query: Dict[str, str] = {}
        response = self.get(AUTH_MAPPING_ROUTE, json=query)
        response.raise_for_status()
        return response.json()['authMappings']

    def __get_all_policy_templates(self):
        response = self.get(AUTH_POLICY_TEMPLATE_ROUTE)
        response.raise_for_status()
        return response.json()['policyTemplates']

    def __get_built_in_policy_templates(self):
        return [policy for policy in self.__get_all_policy_templates() if policy['builtIn']]

    @staticmethod
    def __assert_dictionaries_equal(expected, actual, keys_to_not_compare):
        expected_excluding_ignored = set(expected).difference(keys_to_not_compare)
        actual_excluding_ignored = set(actual).difference(keys_to_not_compare)
        assert all(expected[key] == actual[key] for key in expected_excluding_ignored)
        assert expected_excluding_ignored == actual_excluding_ignored


if __name__ == '__main__':
    handle_command_line(TestSecurity)
