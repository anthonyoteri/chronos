# Copyright (C) 2017, Anthony Oteri.
# All rights reserved.
"""UI Element for controlling the list of projects."""

from __future__ import absolute_import

import logging
import Tkinter as tk
import ttk
import tkMessageBox

from chronos import event
from chronos.db import ProjectService

log = logging.getLogger(__name__)


class Project(ttk.Frame):
    """UI widget for controlling the list of projects."""

    # This needs to be fast, since it's used for determining the selected
    # element.
    POLLING_INTERVAL = 250

    def __init__(self, master):
        """Initialize the layout and internal state."""
        ttk.Frame.__init__(self, master)

        self.project_list = set()
        self.entry = tk.StringVar()
        self.selected = tk.StringVar()

        self.project_service = ProjectService()

        self.configure_layout()
        self.create_widgets()

        self.poll()

        event.register(self.update)

    def configure_layout(self):
        """Configure the grid layout."""

        for row in xrange(24):
            self.rowconfigure(row, weight=1)

        for col in xrange(50):
            self.columnconfigure(col, weight=1)

    def create_widgets(self):
        """Layout the UI elements on the screen."""

        self.box = tk.Listbox(self)
        self.box['relief'] = 'flat'
        self.box.grid(row=0,
                      column=0,
                      rowspan=45,
                      columnspan=24,
                      sticky='news')

        entry = ttk.Entry(self, textvariable=self.entry)
        entry.grid(row=49, column=0, columnspan=16, sticky='sw')
        entry.bind("<Return>", self.on_return)

        self.plus_button = ttk.Button(self,
                                      text='+',
                                      command=self.on_plus,
                                      width=1)
        self.plus_button.grid(row=49, column=16, columnspan=4, sticky='se')

        self.minus_button = ttk.Button(self,
                                       text='-',
                                       command=self.on_minus,
                                       width=1)
        self.minus_button.grid(row=49, column=20, columnspan=4, sticky='se')

    def on_return(self, event):
        """Add the entered text as a new project."""
        if self.entry.get():
            self.on_plus()

    @event.notify
    def on_plus(self):
        """Add the entered text as a new project."""

        new_project = self.entry.get()

        if not new_project:
            log.debug("Nothing was entered.")

        if new_project not in self.project_list:
            log.info("Adding project %s", new_project)
            self.project_service.create(name=new_project)
            self.entry.set('')
        else:
            log.info("Project %s already exists", new_project)

    @event.notify
    def on_minus(self):
        """Remove the currently selected project."""

        def confirm_deletion(target):
            # Prompt the user for confirmation before deleting a project.
            confirmed = tkMessageBox.askyesno(
                "Delete project",
                "Are you sure you want to delete %s?" % target)
            if not confirmed:
                log.info("The delete operation for %s was cancelled by "
                         "the user.", target)
            return confirmed

        target = self.selected.get()
        log.debug("attempt to remove project %s", target)

        if target in self.project_list and confirm_deletion(target):
            try:
                self.project_service.delete(name=target)
            except KeyError as e:
                log.warning("Failed to remove project %s: %s", target, e)
                return
            else:
                log.info("Project %s successfully deleted.", target)
                # Clear the entry box and save the status.
                self.selected.set('')

    @event.notify
    def on_selection(self, selection):
        """Update the current selection and save the status."""
        self.selected.set(selection)

    def load(self):
        """Update the internal data from the database."""

        self.project_list.clear()
        for row in self.project_service.list():
            try:
                self.project_list.add(row['name'])
            except KeyError:
                log.debug("error fetching project, "
                          "database possibly not ready.")

    def update(self):
        """Refresh the UI elements."""
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
        """Poll to check what is selected, and update the button state."""

        active = self.box.get(tk.ACTIVE)
        if self.selected.get() != active:
            self.on_selection(active)

        if self.entry.get():
            self.plus_button['state'] = tk.NORMAL
        else:
            self.plus_button['state'] = tk.DISABLED

        self.after(Project.POLLING_INTERVAL, self.poll)
