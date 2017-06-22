# Copyright (C) 2017, Anthony Oteri
# All rights reserved

from __future__ import absolute_import

import logging as python_logging
from StringIO import StringIO

log = python_logging.getLogger()  # Get the root logger

buffer = StringIO()


def init(level):
    python_logging.basicConfig(level=level)

    global buffer
    console_handler = python_logging.StreamHandler(buffer)
    console_handler.setLevel(level)
    log.addHandler(console_handler)
