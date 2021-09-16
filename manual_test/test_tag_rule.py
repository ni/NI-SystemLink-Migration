from manual_test.manual_test_base import \
    ManualTestBase, \
    handle_command_line, \
    CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.notification_utilities import NotificationUtilities
from manual_test.utilities.workspace_utilities import WorkspaceUtilities
from typing import Any, Dict, List, Optional

SERVICE_NAME = 'TagRuleEngine'
TAG_RULE_DATABASE_NAME = 'nitagrule'
TEST_NAME = 'TagRuleMigrationTest'
TEST_WORKSPACE_NAME = f'CustomWorkspaceFor{TEST_NAME}'
CREATE_TAG_RULE_ROUTE = 'nitagrule/v1/rules'
QUERY_TAG_RULES_ROUTE = 'nitagrule/v1/query-rules'


class TestTagRule(ManualTestBase):
    def populate_data(self) -> None:
        notification_strategy_id = self.__create_test_notification_strategy()
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace(TEST_WORKSPACE_NAME, self)
        for workspace_id in workspace_utilities.get_workspaces(self):
            self.__create_test_rules(workspace_id, notification_strategy_id)

        self.record_json_data(SERVICE_NAME, TAG_RULE_DATABASE_NAME, POPULATED_SERVER_RECORD_TYPE, self.__get_all_rules())

    def record_initial_data(self) -> None:
        self.record_json_data(SERVICE_NAME, TAG_RULE_DATABASE_NAME, CLEAN_SERVER_RECORD_TYPE, self.__get_all_rules())

    def validate_data(self) -> None:
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            TAG_RULE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_json_data(
            SERVICE_NAME,
            TAG_RULE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_snapshot = self.__get_all_rules()

        workspaces = WorkspaceUtilities().get_workspaces(self)
        notification_strategies = NotificationUtilities().get_all_notification_strategies(self)

        migrated_record_count = 0
        for rule in current_snapshot:
            expected_rule = self.find_record_with_matching_id(rule, source_service_snapshot)
            if expected_rule is not None:
                self.__assert_rules_equal(expected_rule, rule)
                self.__assert_rule_has_valid_workspace(rule, workspaces)
                self.__assert_rule_has_valid_notification_strategies(rule, notification_strategies)
                migrated_record_count = migrated_record_count + 1
            else:
                # Verify items that are generated by the target version and not present in the source.
                expected_rule = self.__find_rule_by_display_name(rule, target_service_snaphot)
                assert expected_rule is not None
                self.__assert_rules_equal(expected_rule, rule)
                self.__assert_rule_has_valid_workspace(rule, workspaces)
                self.__assert_rule_has_valid_notification_strategies(rule, notification_strategies)

        assert len(source_service_snapshot) == migrated_record_count

    def __get_all_rules(self) -> List[Dict[str, Any]]:
        # NOTE: workspace="*" does not work as normal for the tag rule API. No value is used for all workspaces.
        query: Dict[str, str] = {}
        response = self.post(QUERY_TAG_RULES_ROUTE, json=query)
        response.raise_for_status()

        return response.json()['rules']

    def __create_test_rules(self, workspace_id: str, notification_strategy_id: str):
        self.__create_test_rule(workspace_id, notification_strategy_id, enabled=True)
        self.__create_test_rule(workspace_id, notification_strategy_id, enabled=False)

    def __create_test_rule(self, workspace_id: str, notification_strategy_id: str, enabled: bool):
        state_description = 'Enabled' if enabled else 'Disabled'
        rule = {
            'searchPath': 'test.tag.for.tag.rule.migration',
            'workspace': workspace_id,
            'tagDataType': 'DOUBLE',
            'conditions': [self.__build_test_rule_condition(notification_strategy_id)],
            'disabled': not enabled,
            'displayName': f'{state_description} Test Tag Rule',
            'description': f'Test tag rule with state set to {state_description} for workspace {workspace_id}',
            'alarmInstanceDisplayNameTemplate': 'Test Tag Rule Alarm',
            'alarmInstanceDescriptionTempalte': 'Alarm created for testing migration of the Tag Rule Engine',
            'keywords': [TEST_NAME],
            'properties': {'forTest': 'True'}
        }
        response = self.post(CREATE_TAG_RULE_ROUTE, retries=self.build_default_400_retry(), json=rule)
        response.raise_for_status()

    def __build_test_rule_condition(self, notification_strategy_id: str) -> Dict[str, Any]:
        return {
            'setPoints': ['0'],
            'comparator': 'LESS_THAN',
            'deadband': '0',
            'securityLevel': '2',
            'notificationStrategyIds': [notification_strategy_id]
        }

    def __create_test_notification_strategy(self) -> str:
        result = NotificationUtilities().create_simple_smtp_notification_strategy(
            self,
            f'Notification strategy for {TEST_NAME}',
            'Test notification strategy')

        return result['notification_strategy']['id']

    def __assert_rules_equal(self, expected: Dict[str, Any], actual: Dict[str, Any]):
        if self.__is_test_rule(expected):
            assert expected == actual
        else:
            # Minimal checks for a rule we didn't create.
            assert expected['displayName'] == actual['displayName']

    def __assert_rule_has_valid_workspace(self, rule: Dict[str, Any], workspaces: List[str]):
        matching_workspace = next((workspace for workspace in workspaces if workspace == rule['workspace']), None)
        assert matching_workspace is not None

    def __assert_rule_has_valid_notification_strategies(
        self,
        rule: Dict[str, Any],
        notification_strategies: List[Dict[str, Any]]
    ):
        for condition in rule['conditions']:
            if self.__is_test_rule(rule):
                assert len(condition['notificationStrategyIds']) > 0

            for strategy_id in condition['notificationStrategyIds']:
                matches = (strategy for strategy in notification_strategies if strategy['id'] == strategy_id)
                assert next(matches, None) is not None

    def __find_rule_by_display_name(
        self,
        rule: Dict[str, Any],
        collection: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        return self.find_record_with_matching_property_value(rule, collection, 'displayName')

    def __is_test_rule(self, rule: Dict[str, Any]) -> bool:
        return 'forTest' in rule['properties']


if __name__ == '__main__':
    handle_command_line(TestTagRule)
