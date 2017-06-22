# Copyright (C) 2017, Anthony Oteri.
# All rights reserved.

from __future__ import absolute_import

import logging
import Tkinter as tk
import ttk
import tkMessageBox

from cronos import event
from cronos.db import ProjectService

log = logging.getLogger(__name__)


class Project(ttk.Frame):

    POLLING_INTERVAL = 250

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        for row in xrange(24):
            self.rowconfigure(row, weight=1)
        for col in xrange(40):
            self.columnconfigure(col, weight=1)

        self.project_list = set()
        self.entry = tk.StringVar()
        self.selected = tk.StringVar()

        self.create_widgets()

        self.project_service = ProjectService()

        event.register(self.update)
        self.poll()

    def create_widgets(self):
        self.box = tk.Listbox(self)
        self.box['relief'] = 'flat'
        self.box.grid(row=0, column=0, rowspan=35, columnspan=24,
                      sticky='news')

        entry = ttk.Entry(self, textvariable=self.entry)
        entry.grid(row=39, column=0, columnspan=16, sticky='sw')
        entry.bind("<Return>", self.on_return)

        self.plus_button = ttk.Button(self, text='+', command=self.on_plus,
                                      width=1)
        self.plus_button.grid(row=39, column=16, columnspan=4, sticky='se')

        self.minus_button = ttk.Button(self, text='-', command=self.on_minus,
                                       width=1)
        self.minus_button.grid(row=39, column=20, columnspan=4, sticky='se')

    def on_return(self, event):
        log.debug("on_return: %r", self)
        if self.entry.get():
            self.on_plus()

    def on_plus(self):
        log.debug("on_plus: %r", self)

        new_project = self.entry.get()
        if new_project not in self.project_list:
            log.debug("Creating new project %s", new_project)
            self.project_service.create(name=new_project)
            self.entry.set('')
            self.save()

    def on_minus(self):
        log.debug("on_minus: %r", self)

        target = self.selected.get()
        if target in self.project_list:
            prompt = tkMessageBox.askyesno(
                "Delete project",
                "Are you sure you want to delete %s?" % target)
            if not prompt:
                log.debug("Cancelled project deletion for %s", target)
                return
            try:
                self.project_service.delete(name=target)
            except KeyError:
                log.warning("Failed to remove project %s", target)
                return
            else:
                self.selected.set('')
                self.save()

    def on_selection(self, selection):
        log.debug("on_selection: selection=%s %r", selection, self)
        self.selected.set(selection)
        self.save()

    def load(self):
        log.debug("load: %r", self)
        self.project_list.clear()
        for row in self.project_service.list():
            try:
                self.project_list.add(row['name'])
            except KeyError:
                continue

    @event.notify
    def save(self):
        log.debug("save: %r", self)

    def update(self):
        log.debug("update: %r", self)
        self.load()

        self.box.delete(0, tk.END)
        for project in sorted(self.project_list):
            self.box.insert(tk.END, project)

        selection = self.selected.get()
        if selection:
            idx = self.box.get(0, tk.END).index(selection)
            self.box.activate(idx)
            self.box.selection_set(idx)
            self.minus_button['state'] = tk.NORMAL
        else:
            self.minus_button['state'] = tk.DISABLED

    def poll(self):
        active = self.box.get(tk.ACTIVE)
        if self.selected.get() != active:
            self.on_selection(active)

        if self.entry.get():
            self.plus_button['state'] = tk.NORMAL
        else:
            self.plus_button['state'] = tk.DISABLED

        self.after(Project.POLLING_INTERVAL, self.poll)

    def validate(self):
        log.debug("validate: %s", self)
        self.box.get(0, tk.END).index(self.entry.get())

    def __repr__(self):
        return "Project[entry=%s, selected=%s]" % (
            self.entry.get(), self.selected.get()
        )


