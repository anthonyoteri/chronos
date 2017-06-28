# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Construct the main application framework."""

from __future__ import absolute_import

import logging
import Tkinter as tk
import ttk

from chronos import __NAME__, __VERSION__, event, config
import chronos.ui

log = logging.getLogger(__name__)


class Application(object):
    """The application."""

    def __init__(self):
        """Initialize the main window, and configure the geometry."""
        log.debug("Creating the application")

        self.window = tk.Tk()
        self.window.title(self.window_title)
        log.info("Available themes %s", ", ".join(ttk.Style().theme_names()))

        theme_name = config.ui('theme')
        if theme_name:
            try:
                ttk.Style().theme_use(theme_name)
            except Exception:
                log.error("No such theme %s", theme_name)

        self.window.geometry('960x500')
        self.configure_grid_layout(self.window, rows=1, cols=1)

        self.content = ttk.Frame(self.window, padding=(3, 3, 12, 12))
        self.content.grid(row=0, column=0, sticky='news')

        # With a window geometry of 960x500, this will result in 50 rows
        # of 10px each vertically, by 24 columns of 40px each horizontally.
        self.configure_grid_layout(self.content, rows=50, cols=24)

        self.create_widgets()
        event.trigger()

    def configure_grid_layout(self, parent, rows, cols, rowsize=1, colsize=1):
        """Configure the grid for the given number of rows and columns."""

        for row in xrange(rows):
            parent.rowconfigure(row, weight=1, minsize=rowsize)

        for col in xrange(cols):
            parent.columnconfigure(col, weight=1, minsize=colsize)

    def create_widgets(self):
        """Create and place the widgets on the screen."""

        # The left notebook contains the read-only viewports for the app.
        left = ttk.Notebook(self.content)
        left.grid(row=0, column=0, rowspan=50, columnspan=15, sticky='news')

        # The right notebook contains the control panes.
        right = ttk.Notebook(self.content)
        right.grid(row=0, column=16, rowspan=50, columnspan=7, sticky='news')

        self.configure_left_notebook(left)
        self.configure_right_notebook(right)

    def configure_left_notebook(self, notebook):
        """Configure the UI tabs on the left notebook."""

        day = chronos.ui.Day(notebook)
        notebook.add(day, text='Day', sticky='news')

        week = chronos.ui.Week(notebook)
        notebook.add(week, text='Week', sticky='news')

        month = chronos.ui.Month(notebook)
        notebook.add(month, text='Month', sticky='news')

        custom = chronos.ui.CustomRange(notebook)
        notebook.add(custom, text='Custom', sticky='news')

        console_log = chronos.ui.Log(notebook)
        notebook.add(console_log, text="Log", sticky='news')

    def configure_right_notebook(self, notebook):
        """Configure the UI tabs on the right notebook."""

        time_clock = chronos.ui.Clock(notebook)
        notebook.add(time_clock, text="Time")

        project = chronos.ui.Project(notebook)
        notebook.add(project, text="Project")

    def run(self):
        """Start the TK framework's main loop, and block forever."""
        self.window.mainloop()

    @property
    def window_title(self):
        """The text to be displayed in the window title."""
        return "%s v.%s" % (__NAME__, __VERSION__)
