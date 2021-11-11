from enum import Enum


class MigrationAction(Enum):
    """
    The command of a migration operation.
    """
    CAPTURE = 0
    RESTORE = 1
    LIST = 2
