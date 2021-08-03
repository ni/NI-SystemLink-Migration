import os
import shutil
import sys
from unittest.mock import patch

import pytest

import slmigrate.argument_handler as arg_handler
import slmigrate.constants as constants
import slmigrate.filehandler as file_handler
from test import test_constants
from .context import systemlinkmigrate

@pytest.mark.unit
def test_parse_arguments():
    """TODO: Complete documentation.

    :return:
    """
    parser = arg_handler.create_nislmigrate_argument_parser()
    assert parser.parse_args(
        [
            constants.CAPTURE_ARG,
            "--" + constants.tag.arg,
            "--" + constants.opc.arg,
            "--" + constants.testmonitor.arg,
            "--" + constants.alarmrule.arg,
            "--" + constants.opc.arg,
            "--" + constants.asset.arg,
            "--" + constants.repository.arg,
            "--" + constants.userdata.arg,
            "--" + constants.notification.arg,
            "--" + constants.states.arg,
        ]
    )