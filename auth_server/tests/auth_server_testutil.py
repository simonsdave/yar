"""This module contains a collection of utilities for
the auth server's unit tests."""

import logging
import os
import socket
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_logger = logging.getLogger(__name__)
