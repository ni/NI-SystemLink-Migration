from typing import Any, Dict, List
from manual_test.manual_test_base import \
    ManualTestBase, \
    handle_command_line, \
    CLEAN_SERVER_RECORD_TYPE, \
    POPULATED_SERVER_RECORD_TYPE

SERVICE_NAME = 'AssetPerformanceManagementRuleEngine'
ASSET_RULE_DATABASE_NAME = 'niapmrule'
TEST_NAME = 'AssetRuleMigrationTest'
GET_CALIBRATION_RULES_ROUTE = 'niapmrule/v1/calibration-rules'
MODIFY_CALIBRATION_RULES_ROUTE_FORMAT = 'niapmrule/v1/calibration-rules/{rule_id}'

class TestAssetRule(ManualTestBase):

    def populate_data(self) -> None:
        pass

    def record_initial_data(self) -> None:
        self.record_json_data(SERVICE_NAME, ASSET_RULE_DATABASE_NAME, CLEAN_SERVER_RECORD_TYPE, self.__get_all_rules())

    def validate_data(self) -> None:
        pass

    def __get_all_rules(self) -> List[Dict[str, Any]]:
        response = self.get(GET_CALIBRATION_RULES_ROUTE)
        response.raise_for_status()

        return response.json()


if __name__ == '__main__':
    handle_command_line(TestAssetRule)