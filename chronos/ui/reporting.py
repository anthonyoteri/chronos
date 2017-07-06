# Copyright (C) 2017, Anthony Oteri.
# All rights reserved
"""Widgets for reporting time."""

from __future__ import absolute_import

import collections
import logging
import time
import Tkinter as tk
import ttk
from datetime import datetime
from dateutil.relativedelta import relativedelta

from chronos import utils
from chronos.db import RecordService

log = logging.getLogger(__name__)


class Report(ttk.Frame):
    """Generic navigable report."""

    POLLING_INTERVAL_MS = 250

    def __init__(self, master):
        """Initialilize the state of the report."""

        ttk.Frame.__init__(self, master)

        self.use_summary = tk.IntVar()
        self.filter_ = tk.StringVar()

        self.text = ''

        # The reference date from which the report will be based.
        self.reference = datetime.today().date()

        # By default, navigation buttons will move the reference date by 1 day.
        self.delta = relativedelta(days=1)

        self.data = collections.defaultdict(list)
        self.record_service = RecordService()

        self.configure_layout()
        self.create_widgets()

        self.poll()

    def configure_layout(self):
        """Configure the grid layout."""
        for row in xrange(50):
            self.rowconfigure(row, weight=1)

        for col in xrange(12):
            self.rowconfigure(col, weight=1)

    def create_widgets(self):
        """Layout the elements on screen."""

        ttk.Label(self, text="Filter").grid(row=0, column=9, sticky='e')
        filter_ = ttk.Entry(self, textvariable=self.filter_)
        filter_.grid(row=0, column=10, columnspan=2, sticky='news')

        self.box = tk.Text(self)
        self.box.grid(row=1,
                      column=0,
                      rowspan=45,
                      columnspan=12,
                      sticky='news')

        self.summary_button = ttk.Checkbutton(self,
                                              text='Summary',
                                              variable=self.use_summary)

        self.summary_button.invoke()
        self.summary_button.grid(row=49, column=0, sticky='news')

        self.back_button = ttk.Button(self, text="<", command=self.back)
        self.back_button.grid(row=49, column=9, sticky='news')

        self.today_button = ttk.Button(self, text="Today", command=self.today)
        self.today_button.grid(row=49, column=10, sticky='news')

        self.forward_button = ttk.Button(self, text=">", command=self.forward)
        self.forward_button.grid(row=49, column=11, sticky='news')

    def back(self):
        """Move the reference date back by `self.delta` units."""
        self.reference -= self.delta

    def today(self):
        """Reset the reference date back to today."""
        self.reference = datetime.today().date()

    def forward(self):
        """Move the reference date forward by `self.delta` units."""
        self.reference += self.delta

    def lines(self):
        """Generate the lines to be displayed in the box."""
        for line in self.text.splitlines():
            yield line

    def load(self):
        """Subclasses should override this to load the data from the DB."""
        pass

    def update(self):
        """Update the displayed contents of the window."""
        self.load()

        self.box['state'] = tk.NORMAL
        self.box.delete(1.0, tk.END)

        for line in self.lines():
            self.box.insert(tk.END, line + "\n")

        # Move the cursor to the end to prevent the display from jumping
        # back to the beginning after each refresh.
        self.box.see(tk.END)

        self.box['state'] = tk.DISABLED

    def poll(self):
        """Repeatedly call the `self.poll()` method."""
        self.text = str(self.reference)
        self.update()

        if self.reference >= datetime.today().date():
            self.forward_button['state'] = tk.DISABLED
        else:
            self.forward_button['state'] = tk.NORMAL

        self.after(self.POLLING_INTERVAL_MS, self.poll)


class Day(Report):
    """Generate a report for a single day."""

    fmt_summary = "  %-30s %-10s"
    fmt_ledger = "  %-30s %-6s %-10s %-10s %-10s"

    def start(self):
        return utils.start_of_day(self.reference)

    def stop(self):
        return utils.end_of_day(self.reference)

    def load(self):
        """Refresh the internal data from the database."""

        filter_ = self.filter_.get()

        try:
            if filter_:
                self.data = self.record_service.by_day(start_date=self.start(),
                                                       stop_date=self.stop(),
                                                       filter_=filter_)
            else:
                self.data = self.record_service.by_day(start_date=self.start(),
                                                       stop_date=self.stop())
        except ValueError:
            self.data = {}

    def _date_header(self):
        """Generate the lines for the date header."""
        try:
            min_day = self.start().date()
            max_day = self.stop().date()
        except ValueError:
            yield "No Data for %s" % str(self.reference)
            return

        # Depending on if the report covers a single day or a range of dates
        # construct the date header line accordingly.
        if min_day == max_day:
            yield min_day.strftime("%A, %B %d, %Y")
        else:
            yield "%s - %s" % (min_day.isoformat(), max_day.isoformat())

    def _column_headings(self):
        """Generate the column headings depending on the mode."""
        if self.use_summary.get():
            yield self.fmt_summary % ("PROJECT", "TIME")
            yield self.fmt_summary % ("-------", "-----")
        else:
            yield self.fmt_ledger % ("PROJECT", "DATE", "START", "STOP",
                                     "TIME")
            yield self.fmt_ledger % ("-------", "----", "-----", "----",
                                     "----")

    def _generate_timesheet(self):
        """Generate the values to be displayed on the timesheet."""
        if self.use_summary.get():
            timesheet = collections.defaultdict(int)
            # Since the data is stored as a list of entries per day, aggregate
            # the total per-project time in a single timesheet.
            for entries in self.data.values():
                for entry in entries:
                    if not entry['elapsed']:
                        entry['elapsed'] = int(time.time()) - entry['start_ts']
                    timesheet[entry['project']] += entry['elapsed']

            for project, elapsed in sorted(timesheet.iteritems()):
                yield project, None, None, None, elapsed

        else:
            # Calculate the time per "punch of the timeclock"
            for entries in self.data.values():
                for entry in entries:
                    start_ts = utils.local_time(datetime.utcfromtimestamp(
                        entry['start_ts']))
                    start = start_ts.time().isoformat()
                    if not entry['elapsed']:
                        stop = '-'
                    else:
                        stop = utils.local_time(datetime.utcfromtimestamp(
                            entry['stop_ts'])).time().isoformat()
                    elapsed = (entry['elapsed'] or
                               int(time.time()) - entry['start_ts'])
                    yield (entry['project'], start_ts.date().strftime('%m-%d'),
                           start, stop, elapsed)

    def _footer(self):
        """Generate the footer lines based on the mode."""
        total = 0
        for entries in self.data.values():
            for entry in entries:
                total += entry['elapsed'] or int(time.time()) - entry[
                    'start_ts']

        if self.use_summary.get():
            yield self.fmt_summary % ('=====', '=====')
            yield self.fmt_summary % ('TOTAL', utils.human_time(total))
        else:
            yield self.fmt_ledger % ('=====', '', '', '', '=====')
            yield self.fmt_ledger % ('TOTAL', '', '', '',
                                     utils.human_time(total, 0))

    def lines(self):
        """Generate the report contents."""

        for line in self._date_header():
            yield line

        for line in self._column_headings():
            yield line

        for (project, start_date, start_time, stop,
             elapsed) in self._generate_timesheet():
            if self.use_summary.get():
                yield self.fmt_summary % (project, utils.human_time(elapsed))
            else:
                yield self.fmt_ledger % (project, start_date, start_time, stop,
                                         utils.human_time(elapsed, 0))

        for line in self._footer():
            yield line


class Week(Day):
    """Generate a report like `Day`, but for the week."""

    def __init__(self, master):
        Day.__init__(self, master)
        self.delta = relativedelta(weeks=1)

    def start(self):
        return utils.start_of_week(self.reference)

    def stop(self):
        return utils.end_of_week(self.reference)


class Month(Day):
    """Generate a report like `Day` but for the month."""

    def __init__(self, master):
        Day.__init__(self, master)
        self.delta = relativedelta(months=1)

    def start(self):
        return utils.start_of_month(self.reference)

    def stop(self):
        return utils.end_of_month(self.reference)


class CustomRange(Day):
    """Generate a report like `Day` but for a user entered date range."""

    def __init__(self, master):
        self.start_entry = tk.StringVar()
        self.stop_entry = tk.StringVar()

        Day.__init__(self, master)

        self.start_entry.set(self.reference.isoformat())
        self.stop_entry.set(self.reference.isoformat())

        self.delta = relativedelta(months=1)

    def create_widgets(self):
        """Extend the `Day.create_widgets()` method.

        Hides the navigation buttons, and replaces them with 2 entry fields
        which should be specified in YYYY-MM-DD format.  The results will
        update as soon as valid values are entered.
        """
        Day.create_widgets(self)

        self.back_button.grid_forget()
        self.today_button.grid_forget()
        self.forward_button.grid_forget()

        ttk.Label(self, text="Start").grid(row=48, column=9, sticky='e')
        ttk.Entry(self, textvariable=self.start_entry).grid(row=48,
                                                            column=10,
                                                            columnspan=2,
                                                            sticky='news')

        ttk.Label(self, text="Stop").grid(row=49, column=9, sticky='e')
        ttk.Entry(self, textvariable=self.stop_entry).grid(row=49,
                                                           column=10,
                                                           columnspan=2,
                                                           sticky='se')

    def start(self):
        return utils.start_of_day(datetime.strptime(self.start_entry.get(),
                                                    '%Y-%m-%d'))

    def stop(self):
        return utils.end_of_day(datetime.strptime(self.stop_entry.get(),
                                                  '%Y-%m-%d'))
