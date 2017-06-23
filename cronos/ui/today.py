# Copyright (C) 2018, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import collections
from datetime import datetime, timedelta
import logging
import time
import Tkinter as tk

from dateutil.relativedelta import relativedelta, MO, SU

from cronos import event
from cronos.db import RecordService
from cronos.ui.console import Console
from cronos.utils import human_time


log = logging.getLogger(__name__)


class Report(Console):

    def __init__(self, master):
        super(Report, self).__init__(master)
        self.data = collections.defaultdict(list)

        self.record_service = RecordService()

        self.polling_interval_ms = 3 * 1000

        event.register(self.update)

    def load(self):
        self.data = self.record_service.by_day(start_date=self._start,
                                               stop_date=self._stop)

    def update(self):
        self.load()

        self.text = '\n'.join(self._make_report())
        self._update()

    def _make_report(self):
        fmt = "  %-25s %s"

        try:
            min_day = min(self.data.keys())
            max_day = max(self.data.keys())
        except ValueError:
            return

        if min_day == max_day:
            yield min_day
        else:
            yield "%s - %s" % (min_day, max_day)

        # Print the header line
        yield fmt % ("PROJECT", "TOTAL TIME")
        yield fmt % ("-------", "----------")

        timesheet = collections.defaultdict(int)

        for entries in self.data.values():
            for entry in entries:
                timesheet[entry['project']] += entry['elapsed']

        for project in sorted(timesheet.keys()):
            if timesheet[project] >= 120:
                yield fmt % (project, human_time(timesheet[project]))

        total = sum(timesheet.values())
        yield fmt % ('=====', '==========')
        yield fmt % ('TOTAL', human_time(total))

    def poll(self):
        try:
            self.update()
        except AttributeError as e:
            log.debug('failed poll attempt due to exception: %s', e)

    @property
    def _start(self):
        return self.start()

    @property
    def _stop(self):
        return self.stop()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def midnight(self, dt):

        if isinstance(dt, datetime):
            dt = dt.date()

        return datetime.combine(dt, datetime.min.time())

    def last_second(self, dt):
        midnight_today = self.midnight(dt)
        midnight_tomorrow = self.midnight(midnight_today + timedelta(days=1))
        return midnight_tomorrow - timedelta(seconds=1)

    def start_of_day(self, dt):
        return self.midnight(dt)

    def end_of_day(self, dt):
        return self.last_second(dt)

    def start_of_month(self, dt):
        return self.midnight(dt.replace(day=1))

    def end_of_month(self, dt):
        first_of_this_month = self.start_of_month(dt)
        first_of_next_month = self.start_of_month(
            first_of_this_month + relativedelta(months=1))
        last_of_this_month = first_of_next_month - timedelta(days=1)

        return self.last_second(last_of_this_month)

    def start_of_week(self, dt):
        monday = dt - relativedelta(weekday=MO(-1))
        return self.midnight(monday)

    def end_of_week(self, dt):
        sunday = dt + relativedelta(weekday=SU)
        return self.last_second(sunday)

class Today(Report):

    def start(self):
        return self.start_of_day(datetime.today())

    def stop(self):
        return self.end_of_day(datetime.today())

class Week(Report):

    def start(self):
        return self.start_of_week(datetime.today())

    def stop(self):
        return self.end_of_week(datetime.today())

class Month(Report):

    def start(self):
        return self.start_of_month(datetime.today())

    def stop(self):
        return self.end_of_month(datetime.today())
