"""Test context."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# This is a workaround due to project structure.
# TODO: replace tests that reference main() with a more sustainable model.
import systemlinkmigrate