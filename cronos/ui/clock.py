# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import logging
import time
import Tkinter as tk
import ttk

from cronos import event
from cronos.db import ProjectService, RecordService
from cronos.utils import human_time


log = logging.getLogger(__name__)


class Clock(ttk.Frame):

    STATUS_RUNNING = "Running"
    STATUS_STOPPED = "Stopped"
    POLLING_INTERVAL_MS = 250

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self.active_project_start_ts = None
        self.active_project = tk.StringVar()
        self.clock_status = tk.StringVar()
        self.elapsed_time = tk.StringVar()

        self.project_service = ProjectService()
        self.record_service = RecordService()

        self.project_list = set()

        self.create_widgets()
        event.register(self.update)

        self.poll()
        self.on_startup()

    def create_widgets(self):
        for row in xrange(40):
            self.rowconfigure(row, weight=1)
        for col in xrange(24):
            self.columnconfigure(col, weight=1)

        ttk.Label(self, text='Clock Status').grid(row=0, column=0,
                                                  columnspan=8, sticky='w')
        ttk.Label(self, textvariable=self.clock_status).grid(
            row=0, column=14, columnspan=10, sticky='w')

        ttk.Label(self, text='Project').grid(
            row=1, column=0, columnspan=8, sticky='w')
        ttk.Label(self, textvariable=self.active_project).grid(
            row=1, column=14, columnspan=10, sticky='w')

        ttk.Label(self, text='Elapsed').grid(
            row=2, column=0, columnspan=8, sticky='w')
        ttk.Label(self, textvariable=self.elapsed_time).grid(
            row=2, column=14, columnspan=10, sticky='w')

        ttk.Label(self, text="Select Project").grid(
            row=38, column=0, columnspan=24, sticky='w')

        self.box = ttk.Combobox(self, textvariable=self.active_project,
                                width=24)
        self.box.grid(row=39, column=0, columnspan=24, sticky='e')

        self.start_button = ttk.Button(self, text='Start',
                                       command=self.on_start)
        self.start_button.grid(row=40, column=12, columnspan=6, sticky='e')

        self.stop_button = ttk.Button(self, text='Stop',
                                      command=self.on_stop)
        self.stop_button.grid(row=40, column=18, columnspan=6, sticky='e')


    @event.notify
    def on_startup(self):
        last_ongoing = self.record_service.ongoing()
        if last_ongoing is not None:
            log.debug("Found existing record for project %s",
                      last_ongoing['project'])
            self.active_project.set(last_ongoing['project'])
            self.active_project_start_ts = last_ongoing['start']

    def load(self):
        log.debug('load: %r', self)

        self.project_list.clear()
        for row in self.project_service.list():
            try:
                self.project_list.add(row['name'])
            except KeyError:
                continue

    def update(self):
        log.debug('update: %r', self)
        self.load()

        self.box['values'] = sorted(self.project_list)

        active_project = self.active_project.get()
        if active_project not in self.project_list:
            self.active_project.set('')
            active_project = None

        if not active_project and self.project_list:
            self.active_project.set([v for v in self.project_list][0])

        if self.running:
            self.start_button['state'] = tk.DISABLED
            self.stop_button['state'] = tk.NORMAL
            self.box['state'] = tk.DISABLED
        else:
            self.start_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.box['state'] = tk.NORMAL

    def poll(self):
        now = time.time()

        if self.running:
            elapsed = int(time.time()) - self.active_project_start_ts
            self.elapsed_time.set(human_time(elapsed, 0))
            self.clock_status.set(Clock.STATUS_RUNNING)
        else:
            self.elapsed_time.set('')
            self.clock_status.set(Clock.STATUS_STOPPED)

        self.after(Clock.POLLING_INTERVAL_MS, self.poll)

    @property
    def running(self):
        return (
            self.active_project.get()
            and self.active_project_start_ts is not None)

    @event.notify
    def on_start(self):
        log.debug('start: %r', self)

        if not self.running:
            self.active_project_start_ts = int(time.time())
            self.record_service.start(
                project=self.active_project.get(),
                ts=self.active_project_start_ts)

    @event.notify
    def on_stop(self):
        log.debug('stop: %r', self)

        if self.running:
            self.record_service.stop(
                project=self.active_project.get(),
                start_ts = self.active_project_start_ts,
                stop_ts = int(time.time()),
            )
            self.active_project_start_ts = None

    def __repr__(self):
        return 'Clock[project=%s, start_ts=%s, elapsed=%s]' % (
            self.active_project.get(),
            self.active_project_start_ts,
            self.elapsed_time.get(),
        )

