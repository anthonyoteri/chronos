# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import logging
import time

from cronos import event
from cronos.logging import buffer
from cronos.ui.console import Console


log = logging.getLogger(__name__)


class Log(Console):

    def __init__(self, master):
        super(Log, self).__init__(master)
        self.polling_interval_ms = 500

        event.register(self.update)

    def update(self):
        self.text = buffer.getvalue()
        self._update()

    def poll(self):
        self.update()
