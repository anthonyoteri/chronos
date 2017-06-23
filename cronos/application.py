# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import logging
import Tkinter as tk
import ttk

from cronos import __NAME__, __VERSION__
import cronos.ui

log = logging.getLogger(__name__)


class Application(object):
    """The application."""

    COLS=24
    ROWS=50

    def __init__(self):
        log.debug("Creating the application")

        self.window = tk.Tk()
        self.window.title(self.window_title)

        self.window.geometry('960x500')
        self.configure_grid_layout(self.window, rows=1, cols=1)

        self.content = ttk.Frame(self.window, padding=(3, 3, 12, 12))
        self.content.grid(row=0, column=0, sticky='news')

        self.configure_grid_layout(self.content, rows=Application.ROWS,
                                   cols=Application.COLS)

        self.create_widgets()

    def configure_grid_layout(self, parent, rows, cols, rowsize=1,
                              colsize=1):
        for row in xrange(rows):
            parent.rowconfigure(row, weight=1, minsize=rowsize)
        for col in xrange(cols):
            parent.columnconfigure(col, weight=1, minsize=colsize)

    def create_widgets(self):

        left = ttk.Notebook(self.content)
        left.grid(row=0, column=0, rowspan=Application.ROWS,
                  columnspan=15, sticky='news')

        right = ttk.Notebook(self.content)
        right.grid(row=0, column=16, rowspan=Application.ROWS,
                   columnspan=7, sticky='news')

        today = cronos.ui.Today(left)
        left.add(today, text='Day')

        week = cronos.ui.Week(left)
        left.add(week, text='Week')

        month = cronos.ui.Month(left)
        left.add(month, text='Month')

        ledger = cronos.ui.Ledger(left)
        left.add(ledger, text="Ledger")

        console_log = cronos.ui.Log(left)
        left.add(console_log, text="Log")

        time_clock = cronos.ui.Clock(right)
        right.add(time_clock, text="Time")

        project = cronos.ui.Project(right)
        right.add(project, text="Project")

    def run(self):
        self.window.mainloop()

    @property
    def window_title(self):
        return "%s v.%s" % (__NAME__, __VERSION__)
