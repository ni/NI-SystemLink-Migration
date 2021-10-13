from typing import Any, Dict, List

from manual_test.manual_test_base import ManualTestBase

QUERY_USER_ROUTE = '/niuser/v1/users/query'


class UserUtilities:

    def get_all_users(self, test: ManualTestBase) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        return test.query_all_with_continuation_token(QUERY_USER_ROUTE, query, 'users')
