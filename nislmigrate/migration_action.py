from enum import Enum


class MigrationAction(Enum):
    CAPTURE = 0
    RESTORE = 1
    # TODO: Remove this when THDBBUG is handled by a plugin.
    THDBBUG = 2
