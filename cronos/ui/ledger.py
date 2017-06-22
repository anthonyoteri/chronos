# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import collections
from datetime import datetime, timedelta
import logging
import time
import Tkinter as tk

from cronos import event
from cronos.db import RecordService
from cronos.ui.console import Console
from cronos.utils import human_time


log = logging.getLogger(__name__)


class Ledger(Console):

    def __init__(self, master):
        super(Ledger, self).__init__(master)
        self.data = collections.defaultdict(list)

        self.record_service = RecordService()

        self.polling_interval_ms = 3 * 1000

        event.register(self.update)

    def load(self):
        self.data = self.record_service.by_day()

    def update(self):
        self.load()

        self.text = '\n'.join(self._make_report())
        self._update()

    def _make_report(self):
        fmt = "  %-25s | %8s | %8s | %s"

        for day, entries in self.data.iteritems():
            yield day
            yield fmt % ("PROJECT", "START", "STOP", "ELAPSED")

            for entry in entries:
                yield fmt % (
                    entry['project'],
                    datetime.fromtimestamp(
                        entry['start_ts']).time().isoformat(),
                    datetime.fromtimestamp(
                        entry['stop_ts']).time().isoformat(),
                    human_time(entry['elapsed'], 0))

    def poll(self):

        try:
            self.update()
        except AttributeError as e:
            log.exception(e)


