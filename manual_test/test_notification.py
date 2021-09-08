import json
from manual_test_base import ManualTestBase, handle_command_line

service_name = 'Notification'
get_address_groups_route = '/ninotification/v1/address-groups'
get_message_templates_route = '/ninotification/v1/message-templates'
get_notification_strategies_route = '/ninotification/v1/notification-strategies'
create_address_group_route ='/ninotification/v1/address-groups'
create_message_templates_route ='/ninotification/v1/message-templates'
create_notification_strategy_route ='/ninotification/v1/notification-strategies'

class TestNotification(ManualTestBase):
    def populate_data(self):
        address_groups = self.__populate_address_groups()
        message_templates = self.__populate_message_templates()
        self.__populate_notification_strategies(address_groups, message_templates)

    def capture_initial_data(self):
        self.write_capture_file(service_name, 'address_groups', self.__get_all_address_groups())
        self.write_capture_file(service_name, 'message_templates', self.__get_all_message_templates())
        self.write_capture_file(service_name, 'notification-strategies', self.__get_all_notification_strategies())

    def validate_data(self):
        return

    def __get_all_address_groups(self) -> list:
        response = self.get(get_address_groups_route)
        response.raise_for_status()

        return response.json()

    def __populate_address_groups(self) -> list:
        created_groups = []
        groups_to_create = self.__get_expected_address_groups()
        for address_group in groups_to_create:
            response = self.post(create_address_group_route, json=address_group)
            response.raise_for_status()
            created_groups.append(response.json())

        return created_groups

    def __get_expected_address_groups(self) -> list:
        address_groups = []
        for i in range(3):
            address_groups.append({
                'interpretingServiceName': 'Smtp',
                'displayName': f'Address Group {i}',
                'fields': self.__get_expected_smtp_address_group_fields(i),
                'properties': { 'forTest': 'True' }
            })

        return address_groups

    def __get_expected_smtp_address_group_fields(self, index) -> dict:
        return {'toAddresses': [f'user{index}@example.com']}

    def __get_all_message_templates(self) -> list:
        response = self.get(get_message_templates_route)
        response.raise_for_status()

        return response.json()

    def __populate_message_templates(self) -> list:
        created_templates = []
        templates_to_create = self.__get_expected_message_templates()
        for template in templates_to_create:
            response = self.post(create_message_templates_route, json=template)
            response.raise_for_status()
            created_templates.append(response.json())

        return created_templates

    def __get_expected_message_templates(self) -> list:
        message_templates = []
        for i in range(5):
            message_templates.append({
                'interpretingServiceName': 'Smtp',
                'displayName': f'Message Template {i}',
                'fields': self.__get_example_smtp_message_template_fields(i),
                'properties': { 'forTest': 'True' }
            })

        return message_templates

    def __get_example_smtp_message_template_fields(self, index) -> dict:
        fields = {}
        fields['subjectTemplate'] = f'Sample subject template {index}'
        fields['bodyTemplate'] = f'Sample body template {index}'

        return fields

    def __get_all_notification_strategies(self) -> list:
        response = self.get(get_notification_strategies_route)
        response.raise_for_status()

        return response.json()

    def __populate_notification_strategies(self, address_groups, message_templates) -> list:
        created_strategies = []
        strategies_to_create = self.__get_expected_notification_strategies(address_groups, message_templates)
        for strategy in strategies_to_create:
            response = self.post(create_notification_strategy_route, json=strategy)
            response.raise_for_status()
            created_strategies.append(response.json())

        return created_strategies

    def __get_expected_notification_strategies(self, address_groups, message_templates) -> list:
        notification_strategies = []
        for i in range(len(address_groups)):
            address_group_id = address_groups[i]['id']
            for j in range(len(message_templates)):
                index = i * len(message_templates) + j
                message_template_id = message_templates[j]['id']
                notification_strategies.append({
                    'displayName': f'Notification Strategy {index}',
                    'description': f'Description {index}',
                    'properties': { 'forTest': 'True' },
                    'notificationConfigurations': [{
                        'addressGroupId': address_group_id,
                        'messageTemplateId': message_template_id
                    }]
                })

        return notification_strategies 

if __name__ == '__main__':
    handle_command_line(TestNotification)
