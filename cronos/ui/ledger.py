# Copyright (C) 2018, Anthony Oteri
# All rights reserved.
"""UI Element for displaying all records for each day."""

from __future__ import absolute_import

import collections
from datetime import datetime, timedelta
import logging
import time
import Tkinter as tk

from cronos import event
from cronos.db import RecordService
from cronos.ui.console import Console
from cronos.utils import human_time, local_time


log = logging.getLogger(__name__)


class Ledger(Console):
    """Widget for displaying a report of all records per day."""

    def __init__(self, master):
        """Construct layout and internal state."""

        super(Ledger, self).__init__(master)

        # A dictionary of day to entries.
        self.data = collections.defaultdict(list)

        self.record_service = RecordService()

        self.polling_interval_ms = 1000

        event.register(self.update)

    def load(self):
        """Load the records from the database."""

        self.data = self.record_service.by_day()

    def update(self):
        """Refresh the output of the report"""
        self.load()

        self.text = '\n'.join(self._make_report())

        # Be sure to redraw the text box.
        self._update()

    def _make_report(self):
        """Generates a report.

        The report will have the following format for each day:

            2017-06-23
              PROJECT         |    START |     STOP | ELAPSED
              foo             | 19:03:27 | 21:05:00 | 01:02
              bar             | 21:06:00 | 21:36:00 | 00:30
              bar             | 21:36:10 | 21:56:00 | 00:20

        Note: Entries less than 2m will be ommitted.
        """

        fmt = "  %-25s | %8s | %8s | %s"

        for day, entries in sorted(self.data.iteritems()):
            yield day
            yield fmt % ("PROJECT", "START", "STOP", "ELAPSED")

            for entry in entries:

                # Skip entries which are insignificant.
                if entry['stop_ts'] - entry['start_ts'] < 120:
                    continue

                yield fmt % (
                    entry['project'],
                    local_time(datetime.utcfromtimestamp(
                        entry['start_ts'])).time().isoformat(),
                    local_time(datetime.utcfromtimestamp(
                        entry['stop_ts'])).time().isoformat(),
                    human_time(entry['elapsed'], 0))
