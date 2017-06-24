# Copyright (C) 2018, Anthony Oteri
# All rights reserved.
"""UI widget for displaying the daily, weekly, and monthly reports."""

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
    """Base class for all reports."""

    def __init__(self, master):
        """Initialize the object state."""

        super(Report, self).__init__(master)

        self.data = collections.defaultdict(list)
        self.reference_point = datetime.today()

        self.record_service = RecordService()

        # Reports should update periodically.
        self.polling_interval_ms = 3 * 1000

        event.register(self.update)

    def load(self):
        """Refresh the internal data from the database."""

        self.data = self.record_service.by_day(start_date=self._start,
                                               stop_date=self._stop)

    def update(self):
        """Refresh the contents of the report."""

        self.load()

        self.text = '\n'.join(self._make_report())

        # Ensure we update the text widget.
        self._update()

    def _make_report(self):
        """Generate the report contents.

        The report will show the total time for each project during the
        reporting period rounded off slightly.  (15 minutes is the default).
        At the end of the report will be a line with the total of all
        projects within the reporting period.

        Any project with a total time less than 2 minutes during the period
        will not be included in the report.
        """

        fmt = "  %-25s %s"

        try:
            min_day = min(self.data.keys())
            max_day = max(self.data.keys())
        except ValueError:
            return

        # Depending on if the report covers a single day or a range of dates
        # construct the date header line accordingly.
        if min_day == max_day:
            yield min_day
        else:
            yield "%s - %s" % (min_day, max_day)

        # Construct the column headings
        yield fmt % ("PROJECT", "TOTAL TIME")
        yield fmt % ("-------", "----------")

        # Since the data is stored as a list of entries per day, aggregate
        # the total per-project time in a single timesheet.
        timesheet = collections.defaultdict(int)
        for entries in self.data.values():
            for entry in entries:
                timesheet[entry['project']] += entry['elapsed']

        # Iterate through the set of projects and yield one line per project
        # to the final report.  Times are rounded based on the `human_time()`
        # function. (Defaults to 15 minutes)
        for project in sorted(timesheet.keys()):
            if timesheet[project] >= 120:
                yield fmt % (project, human_time(timesheet[project]))

        # Calculate and report the total time in the timesheet.
        total = sum(timesheet.values())
        yield fmt % ('=====', '==========')
        yield fmt % ('TOTAL', human_time(total))

    def poll(self):
        """Continuously update the report."""
        try:
            self.update()
        except AttributeError:
            pass

    @property
    def _start(self):
        return self.start()

    @property
    def _stop(self):
        return self.stop()

    def start(self):
        """Return the start time (inclusive) as a datetime."""
        raise NotImplementedError()

    def stop(self):
        """Return the stop time (inclusive) as a datetime."""
        raise NotImplementedError()

    def midnight(self, dt):
        """Return a datetime representing midnight of the given datetime.

        :param date|datetime dt: A date or datetime object as the reference.
        :return datetime:
        """

        if isinstance(dt, datetime):
            dt = dt.date()

        return datetime.combine(dt, datetime.min.time())

    def last_second(self, dt):
        """Return a datetime representing the final second of the day."""

        midnight_today = self.midnight(dt)
        midnight_tomorrow = self.midnight(midnight_today + timedelta(days=1))
        return midnight_tomorrow - timedelta(seconds=1)

    def start_of_day(self, dt):
        """Return the first second in the day."""
        return self.midnight(dt)

    def end_of_day(self, dt):
        """Return the last second in the day."""
        return self.last_second(dt)

    def start_of_month(self, dt):
        """Return the first second of the first day of the month."""
        return self.midnight(dt.replace(day=1))

    def end_of_month(self, dt):
        """Return the last second of the final day of the month."""
        first_of_this_month = self.start_of_month(dt)
        first_of_next_month = self.start_of_month(
            first_of_this_month + relativedelta(months=1))
        last_of_this_month = first_of_next_month - timedelta(days=1)

        return self.last_second(last_of_this_month)

    def start_of_week(self, dt):
        """Return the first second of the Monday of the given week."""
        monday = dt - relativedelta(weekday=MO(-1))
        return self.midnight(monday)

    def end_of_week(self, dt):
        """Return the last second of the Sunday of the given week."""
        sunday = dt + relativedelta(weekday=SU)
        return self.last_second(sunday)


class Today(Report):
    """A report for records in a single day."""

    def start(self):
        return self.start_of_day(self.reference_point)

    def stop(self):
        return self.end_of_day(self.reference_point)

class Week(Report):
    """A report for records in a single week."""

    def start(self):
        return self.start_of_week(self.reference_point)

    def stop(self):
        return self.end_of_week(self.reference_point)

class Month(Report):
    """A report for records in a single month."""

    def start(self):
        return self.start_of_month(self.reference_point)

    def stop(self):
        return self.end_of_month(self.reference_point)
