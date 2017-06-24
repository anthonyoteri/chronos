# Copyright (C) 2017, Anthony Oteri
# All rights reserved
"""Handle capturing the log to an internal variable."""

from __future__ import absolute_import

import logging as python_logging
from StringIO import StringIO

MAX_LINES = 100
log = python_logging.getLogger()  # Get the root logger
buffer = StringIO()


def init(level):
    """Initialize capturing console log handler."""

    python_logging.basicConfig(level=level)

    global buffer
    console_handler = python_logging.StreamHandler(buffer)
    console_handler.setLevel(level)
    log.addHandler(console_handler)


def fetch(lines=MAX_LINES):
    """Fetch the last `lines` lines of the log file."""
    current = buffer.getvalue().splitlines()[-lines:]
    return '\n'.join(current)
