# Copyright (C) 2017, Anthony Oteri.
# All rights reserved.

import logging
import Tkinter as tk
import ttk
import tkMessageBox

from cronos import event


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
        self._dirty = False

        event.register(self.update)

        self.update()
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
            self.project_list.add(new_project)
            self.entry.set('')
            self._dirty = True
            self.update()

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
                self.project_list.remove(target)
            except KeyError:
                log.warning("Failed to remove project %s", target)
                return
            else:
                self._dirty = True
                self.selected.set('')
                self.update()

    def on_selection(self, selection):
        log.debug("on_selection: selection=%s %r", selection, self)
        self.selected.set(selection)
        self._dirty = True
        self.update()

    def load(self):
        log.debug("load: %r", self)

    def save(self):
        log.debug("save: %r", self)
        if self._dirty:
            self._dirty = False
            event.notify()

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

        self.save()

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


