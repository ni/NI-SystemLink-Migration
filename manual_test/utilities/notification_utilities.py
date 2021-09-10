from typing import Any, Dict, List
from manual_test.manual_test_base import ManualTestBase

GET_ADDRESS_GROUPS_ROUTE = '/ninotification/v1/address-groups'
GET_MESSAGE_TEMPLATES_ROUTE = '/ninotification/v1/message-templates'
GET_NOTIFICATION_STRATEGIES_ROUTE = '/ninotification/v1/notification-strategies'
CREATE_ADDRESS_GROUP_ROUTE = '/ninotification/v1/address-groups'
CREATE_MESSAGE_TEMPLATE_ROUTE = '/ninotification/v1/message-templates'
CREATE_NOTIFICATION_STRATEGY_ROUTE = '/ninotification/v1/notification-strategies'


class NotificationUtilities:
    def get_all_address_groups(self, test: ManualTestBase) -> List[Dict[str, str]]:
        response = test.get(GET_ADDRESS_GROUPS_ROUTE)
        response.raise_for_status()
        return response.json()

    def create_address_group(self, test: ManualTestBase, address_group: Dict[str, Any]) -> Dict[str, str]:
        response = test.post(CREATE_ADDRESS_GROUP_ROUTE, json=address_group)
        response.raise_for_status()
        return response.json()

    def build_smtp_address_group_fields(self, addresses: List[str]) -> Dict[str, Any]:
        return {'toAddresses': addresses}

    def get_all_message_templates(self, test: ManualTestBase) -> List[Dict[str, str]]:
        response = test.get(GET_MESSAGE_TEMPLATES_ROUTE)
        response.raise_for_status()
        return response.json()

    def create_message_template(self, test: ManualTestBase, message_template: Dict[str, Any]) -> Dict[str, str]:
        response = test.post(CREATE_MESSAGE_TEMPLATE_ROUTE, json=message_template)
        response.raise_for_status()
        return response.json()

    def build_smtp_message_template_fields(self, subject: str, body: str) -> Dict[str, Any]:
        return {
            'subjectTemplate': subject,
            'bodyTemplate': body
        }

    def get_all_notification_strategies(self, test: ManualTestBase) -> List[Dict[str, str]]:
        response = test.get(GET_NOTIFICATION_STRATEGIES_ROUTE)
        response.raise_for_status()
        return response.json()

    def create_notification_strategy(
            self,
            test: ManualTestBase,
            notification_strategy: Dict[str, Any]
    ) -> Dict[str, str]:
        response = test.post(CREATE_NOTIFICATION_STRATEGY_ROUTE, json=notification_strategy)
        response.raise_for_status()
        return response.json()

    def create_simple_smtp_notification_strategy(
            self,
            test: ManualTestBase,
            displayName: str,
            description: str = '',
            addresses: List[str] = [],
            subject: str = 'Test Notification',
            body: str = 'Test Notification'
    ) -> Dict[str, Dict[str, str]]:
        result = {}
        address_group = {
            'interpretingServiceName': 'Smtp',
            'displayName': f'Address Group for "{displayName}"',
            'fields': self.build_smtp_address_group_fields(addresses),
            'properties': {'forTest': 'True'}
        }
        result['address_group'] = self.create_address_group(test, address_group)

        message_template = {
            'interpretingServiceName': 'Smtp',
            'displayName': f'Message Template for "{displayName}"',
            'fields': self.build_smtp_message_template_fields(subject, body),
            'properties': {'forTest': 'True'}
        }
        result['message_template'] = self.create_message_template(test, message_template)

        notification_strategy = {
            'displayName': displayName,
            'description': description,
            'properties': {'forTest': 'True'},
            'notificationConfigurations': [{
                'addressGroupId': result['address_group']['id'],
                'messageTemplateId': result['message_template']['id'],
                'isExpanded': False,
                'addressGroup': None,
                'messageTemplate': None
            }]
        }
        result['notification_strategy'] = self.create_notification_strategy(test, notification_strategy)

        return result
