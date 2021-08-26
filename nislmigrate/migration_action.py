from enum import Enum


class MigrationAction(Enum):
    """
    The directionality of a migration operation.
    """
    CAPTURE = 0
    RESTORE = 1
