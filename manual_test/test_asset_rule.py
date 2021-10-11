from typing import Any, Dict, List
from manual_test.manual_test_base import \
    ManualTestBase, \
    handle_command_line, \
    CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE
from manual_test.utilities.notification_utilities import NotificationUtilities
from manual_test.utilities.workspace_utilities import WorkspaceUtilities

SERVICE_NAME = 'AssetPerformanceManagementRuleEngine'
ASSET_RULE_DATABASE_NAME = 'niapmrule'
TEST_NAME = 'AssetRuleMigrationTest'
GET_CALIBRATION_RULES_ROUTE = 'niapmrule/v1/calibration-rules'
MODIFY_CALIBRATION_RULES_ROUTE_FORMAT = 'niapmrule/v1/calibration-rules/{rule_id}'

class TestAssetRule(ManualTestBase):

    def populate_data(self) -> None:
        notification_strategy_id = self.__create_test_notification_strategy()
        workspace_utilities = WorkspaceUtilities()
        workspace_utilities.create_workspace_for_test(self)

        # The API does not allow us to create new rules, so add a new handler
        # to the existing rules.
        existing_rules = self.__get_all_rules()
        for workspace_id in workspace_utilities.get_workspaces(self):
            self.__modify_existing_rule(workspace_id, notification_strategy_id, existing_rules)

        self.record_json_data(
            SERVICE_NAME,
            ASSET_RULE_DATABASE_NAME,
            POPULATED_SERVER_RECORD_TYPE,
            self.__get_all_rules())

    def record_initial_data(self) -> None:
        self.record_json_data(
            SERVICE_NAME,
            ASSET_RULE_DATABASE_NAME,
            CLEAN_SERVER_RECORD_TYPE,
            self.__get_all_rules())

    def validate_data(self) -> None:
        pass

    def __get_all_rules(self) -> List[Dict[str, Any]]:
        response = self.get(GET_CALIBRATION_RULES_ROUTE)
        response.raise_for_status()

        return response.json()['calibrationRules']

    def __create_test_notification_strategy(self) -> str:
        result = NotificationUtilities().create_simple_smtp_notification_strategy(
            self,
            f'Notification strategy for {TEST_NAME}',
            'Test notification strategy')

        return result['notification_strategy']['id']

    def __modify_existing_rule(
        self,
        workspace_id: str,
        notification_strategy_id: str,
        existing_rules: List[Dict[str, Any]]
    ):
        existing_rule = self.__find_calibration_rule_for_workspace(workspace_id, existing_rules)
        # severity_levels = existing_rule['severityLevels']
        existing_rule['severityLevels'].append(self.__create_test_severity_level(notification_strategy_id))

        uri = MODIFY_CALIBRATION_RULES_ROUTE_FORMAT.format(rule_id=existing_rule['id'])

        response = self.put(uri, json=existing_rule)
        response.raise_for_status()

    def __create_test_severity_level(self, notification_strategy_id: str) -> Dict[str, Any]:
        return {
            'name': 'Test',
            'severityLevel': 1,
            'daysUntilCalibrationDue': 1,
            'notificationStrategyIds': [notification_strategy_id]
        }

    def __find_calibration_rule_for_workspace(
        self,
        workspace_id: str,
        rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return next((rule for rule in rules if self.__is_calibration_rule_for_workspace(workspace_id, rule)), None)

    def __is_calibration_rule_for_workspace(self, workspace_id: str, rule: Dict[str, Any]) -> bool:
        return rule['displayName'] == 'Calibration' and rule['workspace'] == workspace_id


if __name__ == '__main__':
    handle_command_line(TestAssetRule)