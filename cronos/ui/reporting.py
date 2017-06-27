# Copyright (C) 2017, Anthony Oteri.
# All rights reserved
"""Widgets for reporting time."""

from __future__ import absolute_import

import collections
import logging
import time
import Tkinter as tk
import ttk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO, SU

from cronos import event
from cronos.db import RecordService
from cronos.utils import human_time, local_time


log = logging.getLogger(__name__)


class Console(ttk.Frame, object):
    """Widget for displaying text in a console."""

    POLLING_INTERVAL_MS = 250

    def __init__(self, master):
        """Construct the layout and initialize internal state."""
        ttk.Frame.__init__(self, master)

        self._text = ''

        # Allow subclasses to override the polling interval.
        self.polling_interval_ms = Console.POLLING_INTERVAL_MS

        self.configure_layout()
        self.create_widgets()
        self._poll()

    def configure_layout(self):
        """Configure the grid layout."""
        for row in xrange(50):
            self.rowconfigure(row, weight=1)

        for col in xrange(24):
            self.rowconfigure(col, weight=1)

    def create_widgets(self):
        """Layout the elements on screen."""

        self.box = tk.Text(self)
        self.box.grid(row=0, column=0, rowspan=50, columnspan=24,
                      sticky='news')

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        """Set the text to be displayed in the window."""
        self._text = str(value)

    def _update(self):
        """Update the displayed contents of the window."""

        self.box['state'] = tk.NORMAL
        self.box.delete(1.0, tk.END)

        for line in self._text.splitlines():
            self.box.insert(tk.END, line + "\n")

        # Move the cursor to the end to prevent the display from jumping
        # back to the beginning after each refresh.
        self.box.see(tk.END)

        self.box['state'] = tk.DISABLED

    def _poll(self):
        """Repeatedly call the `self.poll()` method."""

        self.poll()
        self.after(self.polling_interval_ms, self._poll)

    def poll(self):
        """Method to perform the actual polling work.

        Subclasses should override this method to contain whatever work needs
        to be performed periodically.  Adjust the `self.polling_interval_ms`
        variable to control how often this code is executed.
        """
        pass


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
        running_project = None
        for entries in self.data.values():
            for entry in entries:
                if not entry['elapsed']:
                    entry['elapsed'] = int(time.time()) - entry['start_ts']
                    running_project = entry['project']
                timesheet[entry['project']] += entry['elapsed']

        # Iterate through the set of projects and yield one line per project
        # to the final report.  Times are rounded based on the `human_time()`
        # function. (Defaults to 15 minutes)
        for project in sorted(timesheet.keys()):
            if timesheet[project] >= 120:

                marker = ''
                # If the active project is running, mark it with an *
                if project == running_project:
                    marker = '*'

                yield fmt % (project, human_time(timesheet[project]) + marker)

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

