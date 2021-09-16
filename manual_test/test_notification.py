from typing import Any, Dict, List
from manual_test.utilities.notification_utilities import NotificationUtilities
from manual_test.manual_test_base import ManualTestBase, handle_command_line, CLEAN_SERVER_RECORD_TYPE
from manual_test.manual_test_base import POPULATED_SERVER_RECORD_TYPE

SERVICE_NAME = 'Notification'


class TestNotification(ManualTestBase):
    def populate_data(self):
        address_groups = self.__populate_address_groups()
        message_templates = self.__populate_message_templates()
        self.__populate_notification_strategies(address_groups, message_templates)
        self.__record_data(POPULATED_SERVER_RECORD_TYPE)

    def record_initial_data(self):
        self.__record_data(CLEAN_SERVER_RECORD_TYPE)

    def validate_data(self):
        self.__validate_address_groups()
        self.__validate_message_templates()
        self.__validate_notification_strategies()

    def __record_data(self, record_type: str):
        self.record_json_data(
            SERVICE_NAME,
            'address_groups',
            record_type,
            NotificationUtilities().get_all_address_groups(self))
        self.record_json_data(
            SERVICE_NAME,
            'message_templates',
            record_type,
            NotificationUtilities().get_all_message_templates(self))
        self.record_json_data(
            SERVICE_NAME,
            'notification_strategies',
            record_type,
            NotificationUtilities().get_all_notification_strategies(self))

    def __populate_address_groups(self) -> List[Dict[str, str]]:
        created_groups = []
        groups_to_create = self.__get_expected_address_groups()
        for address_group in groups_to_create:
            result = NotificationUtilities().create_address_group(self, address_group)
            created_groups.append(result)

        return created_groups

    def __validate_address_groups(self):
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            'address_groups',
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_json_data(
            SERVICE_NAME,
            'address_groups',
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_snapshot = NotificationUtilities().get_all_address_groups(self)

        migrated_record_count = 0
        for group in current_snapshot:
            expected_group = self.find_record_with_matching_id(group, source_service_snapshot)
            if expected_group is not None:
                self.__assert_address_groups_equal(expected_group, group, exact=True)
                migrated_record_count = migrated_record_count + 1
            else:
                # Verify items that are generated by the target version and not present in the source.
                expected_group = self.find_record_with_matching_id(group, target_service_snaphot)
                assert expected_group is not None
                self.__assert_address_groups_equal(expected_group, group, exact=False)

        assert len(source_service_snapshot) == migrated_record_count

    def __get_expected_address_groups(self) -> List[Dict[str, Any]]:
        address_groups = []
        for i in range(3):
            address_groups.append({
                'interpretingServiceName': 'Smtp',
                'displayName': f'Address Group {i}',
                'fields': self.__get_expected_smtp_address_group_fields(i),
                'properties': {'forTest': 'True'}
            })

        return address_groups

    def __assert_address_groups_equal(self, expected: Dict[str, Any], actual: Dict[str, Any], exact: bool):
        if exact:
            assert expected == actual
        else:
            assert expected['interpretingServiceName'] == actual['interpretingServiceName']
            assert expected['displayName'] == actual['displayName']
            assert expected['fields'] == actual['fields']
            assert expected['properties'] == actual['properties']

    def __get_expected_smtp_address_group_fields(self, index) -> Dict[str, str]:
        addresses = [f'user{index}@example.com']
        return NotificationUtilities().build_smtp_address_group_fields(addresses)

    def __populate_message_templates(self) -> List[Dict[str, str]]:
        created_templates = []
        templates_to_create = self.__get_expected_message_templates()
        for template in templates_to_create:
            result = NotificationUtilities().create_message_template(self, template)
            created_templates.append(result)

        return created_templates

    def __validate_message_templates(self):
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            'message_templates',
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_json_data(
            SERVICE_NAME,
            'message_templates',
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_snapshot = NotificationUtilities().get_all_message_templates(self)

        migrated_record_count = 0
        for template in current_snapshot:
            expected_template = self.find_record_with_matching_id(template, source_service_snapshot)
            if expected_template is not None:
                self.__assert_message_templates_equal(expected_template, template, exact=True)
                migrated_record_count = migrated_record_count + 1
            else:
                # Verify items that are generated by the target version and not present in the source.
                expected_template = self.find_record_with_matching_id(template, target_service_snaphot)
                assert expected_template is not None
                self.__assert_message_templates_equal(expected_template, template, exact=False)

        assert len(source_service_snapshot) == migrated_record_count

    def __get_expected_message_templates(self) -> List[Dict[str, Any]]:
        message_templates = []
        for i in range(5):
            message_templates.append({
                'interpretingServiceName': 'Smtp',
                'displayName': f'Message Template {i}',
                'fields': self.__get_example_smtp_message_template_fields(i),
                'properties': {'forTest': 'True'}
            })

        return message_templates

    def __assert_message_templates_equal(self, expected: Dict[str, Any], actual: Dict[str, Any], exact: bool):
        if exact:
            assert expected == actual
        else:
            assert expected['interpretingServiceName'] == actual['interpretingServiceName']
            assert expected['displayName'] == actual['displayName']
            assert expected['fields'] == actual['fields']
            assert expected['properties'] == actual['properties']

    def __get_example_smtp_message_template_fields(self, index) -> Dict[str, Any]:
        return NotificationUtilities().build_smtp_message_template_fields(
            f'Sample subject template {index}',
            f'Sample body template {index}')

    def __populate_notification_strategies(
            self,
            address_groups: List[Dict[str, Any]],
            message_templates: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        created_strategies = []
        strategies_to_create = self.__get_expected_notification_strategies(address_groups, message_templates)
        for strategy in strategies_to_create:
            result = NotificationUtilities().create_notification_strategy(self, strategy)
            created_strategies.append(result)

        return created_strategies

    def __validate_notification_strategies(self):
        source_service_snapshot = self.read_recorded_json_data(
            SERVICE_NAME,
            'notification_strategies',
            POPULATED_SERVER_RECORD_TYPE,
            required=True)
        target_service_snaphot = self.read_recorded_json_data(
            SERVICE_NAME,
            'notification_strategies',
            CLEAN_SERVER_RECORD_TYPE,
            required=False)
        current_snapshot = NotificationUtilities().get_all_notification_strategies(self)

        migrated_record_count = 0
        for strategy in current_snapshot:
            expected_strategy = self.find_record_with_matching_id(strategy, source_service_snapshot)
            if expected_strategy is not None:
                self.__assert_notification_strategies_equal(expected_strategy, strategy, exact=True)
                migrated_record_count = migrated_record_count + 1
            else:
                # Verify items that are generated by the target version and not present in the source.
                expected_strategy = self.find_record_with_matching_id(strategy, target_service_snaphot)
                assert expected_strategy is not None
                self.__assert_notification_strategies_equal(expected_strategy, strategy, exact=False)

        assert len(source_service_snapshot) == migrated_record_count

    def __get_expected_notification_strategies(
            self,
            address_groups: List[Dict[str, Any]],
            message_templates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        notification_strategies = []
        for i in range(len(address_groups)):
            address_group_id = address_groups[i]['id']
            for j in range(len(message_templates)):
                index = i * len(message_templates) + j
                message_template_id = message_templates[j]['id']
                notification_strategies.append({
                    'displayName': f'Notification Strategy {index}',
                    'description': f'Description {index}',
                    'properties': {'forTest': 'True'},
                    'notificationConfigurations': [{
                        'addressGroupId': address_group_id,
                        'messageTemplateId': message_template_id,
                        'isExpanded': False,
                        'addressGroup': None,
                        'messageTemplate': None
                    }]
                })

        return notification_strategies

    def __assert_notification_strategies_equal(self, expected: Dict[str, Any], actual: Dict[str, Any], exact: bool):
        if exact:
            assert expected == actual
        else:
            assert expected['displayName'] == actual['displayName']
            assert expected['description'] == actual['description']
            assert expected['properties'] == actual['properties']


if __name__ == '__main__':
    handle_command_line(TestNotification)
