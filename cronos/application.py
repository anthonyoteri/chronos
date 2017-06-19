# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

import logging
import Tkinter as tk

from cronos import __NAME__, __VERSION__
import cronos.ui

log = logging.getLogger(__name__)
_the_app = None


class Application(object):
    """The application."""

    def __init__(self):
        log.debug("Creating the application")

        parent = tk.Tk()
        parent.title(self.window_title)

        self.root = Window(parent)
        self.root.pack()

        # Set a global reference to the app
        global _the_app
        _the_app = self

        parent.mainloop()

    @property
    def window_title(self):
        return "%s v.%s" % (__NAME__, __VERSION__)


class Window(tk.Frame):
    """The main frame."""

    def __init__(self, master):
        log.debug("Creating the main window.")
        tk.Frame.__init__(self, master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        project_selector = cronos.ui.Selector(self)
        project_selector.pack()

