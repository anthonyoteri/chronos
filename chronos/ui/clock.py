# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Control panel for the time clock."""

from __future__ import absolute_import

import logging
import time
import Tkinter as tk
import ttk
from datetime import datetime

from chronos import event
from chronos.db import ProjectService, RecordService
from chronos.utils import human_time

log = logging.getLogger(__name__)


class Clock(ttk.Frame):
    """Frame which allows the user to start/stop the timeclock."""

    POLLING_INTERVAL_MS = 250

    def __init__(self, master):
        """Construct the frame and initialize the internal state."""
        ttk.Frame.__init__(self, master)

        self.project_list = set()
        self.active_project_start_ts = None
        self.clock_status = tk.StringVar()
        self.active_project = tk.StringVar()
        self.elapsed_time = tk.StringVar()

        # TODO: Use dependency injection for these services.
        self.project_service = ProjectService()
        self.record_service = RecordService()

        self.configure_layout()
        self.create_widgets()
        self.poll()
        self.on_startup()

        event.register(self.update)

    def configure_layout(self):
        for row in xrange(50):
            self.rowconfigure(row, weight=1)
        for col in xrange(24):
            self.columnconfigure(col, weight=1)

    def create_widgets(self):
        """Construct and place the UI widgets on screen."""

        ttk.Label(self, text='Clock Status').grid(row=0,
                                                  column=0,
                                                  columnspan=8,
                                                  sticky='w')
        ttk.Label(self, textvariable=self.clock_status).grid(row=0,
                                                             column=14,
                                                             columnspan=10,
                                                             sticky='w')

        ttk.Label(self, text='Project').grid(row=1,
                                             column=0,
                                             columnspan=8,
                                             sticky='w')
        ttk.Label(self, textvariable=self.active_project).grid(row=1,
                                                               column=14,
                                                               columnspan=10,
                                                               sticky='w')

        ttk.Label(self, text='Elapsed').grid(row=2,
                                             column=0,
                                             columnspan=8,
                                             sticky='w')
        ttk.Label(self, textvariable=self.elapsed_time).grid(row=2,
                                                             column=14,
                                                             columnspan=10,
                                                             sticky='w')

        ttk.Label(self, text="Select Project").grid(row=48,
                                                    column=0,
                                                    columnspan=24,
                                                    sticky='w')

        self.box = ttk.Combobox(self,
                                textvariable=self.active_project,
                                width=24)
        self.box.grid(row=49, column=0, columnspan=24, sticky='e')

        self.start_button = ttk.Button(self,
                                       text='Start',
                                       command=self.on_start)
        self.start_button.grid(row=50, column=12, columnspan=6, sticky='e')

        self.stop_button = ttk.Button(self, text='Stop', command=self.on_stop)
        self.stop_button.grid(row=50, column=18, columnspan=6, sticky='e')

    @event.notify
    def on_startup(self):
        """Determine status of last exit and set the state accordingly."""
        last_ongoing = self.record_service.ongoing()

        if last_ongoing is not None:
            log.info("Resuming active project %s, started at %s",
                     last_ongoing['project'],
                     str(datetime.utcfromtimestamp(last_ongoing['start'])))

            self.active_project.set(last_ongoing['project'])
            self.active_project_start_ts = last_ongoing['start']

    def load(self):
        """Load the project list from the database."""
        self.project_list.clear()
        for row in self.project_service.list():
            try:
                self.project_list.add(row['name'])
            except KeyError:
                log.debug("The database may not be ready.")
                continue

    def update(self):
        """Refresh the internal state of the object from the database."""
        self.load()

        # Reset the list of projects displayed in the dropdown.
        self.box['values'] = sorted(self.project_list)

        # Handle the case where the active project has been deleted, in that
        # case, we need to clear the active project field.
        if self.active_project.get() not in self.project_list:
            self.active_project.set('')

        # If the active project field is not set, but we have a list of
        # projects, set the active project to the first project in the list.
        if not self.active_project.get() and self.project_list:
            self.active_project.set([v for v in self.project_list][0])

        # Toggle the enabled/disabled state of the buttons depending on if
        # the clock is currently running.
        if self.running:
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.NORMAL
            self.box['state'] = tk.DISABLED
        else:
            self.start_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.box['state'] = tk.NORMAL

    def poll(self):
        """Update the displayed times so that the fields work in real-time."""
        now = int(time.time())

        if self.running:
            elapsed = time.time() - self.active_project_start_ts
            self.elapsed_time.set(human_time(elapsed, 0))
            self.clock_status.set("Running")
        else:
            self.elapsed_time.set('')
            self.clock_status.set("Stopped")

        self.after(Clock.POLLING_INTERVAL_MS, self.poll)

    @property
    def running(self):
        """Return true if an active project has been started."""
        return (self.active_project.get() and
                self.active_project_start_ts is not None)

    @event.notify
    def on_start(self):
        """Start the clock on the current active project."""

        if not self.running:
            log.info("Starting work on project %s at %s",
                     self.active_project.get(), str(datetime.now()))

            self.active_project_start_ts = int(time.time())
            log.debug("active project start timestamp %d",
                      self.active_project_start_ts)

            self.record_service.start(project=self.active_project.get(),
                                      ts=self.active_project_start_ts)

    @event.notify
    def on_stop(self):
        """Stop the clock on the current active project."""

        if self.running:
            log.info("Stopping work on project %s at %s",
                     self.active_project.get(), str(datetime.now()))

            stop_ts = int(time.time())
            log.debug("active project stop timestamp %d", stop_ts)

            self.record_service.stop(project=self.active_project.get(),
                                     start_ts=self.active_project_start_ts,
                                     stop_ts=stop_ts, )

            self.active_project_start_ts = None
