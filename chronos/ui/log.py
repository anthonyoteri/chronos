# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""UI element for displaying the current log."""

from __future__ import absolute_import

import logging
import Tkinter as tk
import ttk

from chronos import event
from chronos.logging import fetch

log = logging.getLogger(__name__)


class Log(ttk.Frame, object):
    """Widget for displaying text in a console."""

    POLLING_INTERVAL_MS = 3 * 1000

    def __init__(self, master):
        """Construct the layout and initialize internal state."""
        ttk.Frame.__init__(self, master)

        self._text = ''

        # Allow subclasses to override the polling interval.
        self.polling_interval_ms = Log.POLLING_INTERVAL_MS

        self.configure_layout()
        self.create_widgets()
        self.poll()

        event.register(self.update)

    def configure_layout(self):
        """Configure the grid layout."""
        for row in xrange(50):
            self.rowconfigure(row, weight=1)

        for col in xrange(24):
            self.rowconfigure(col, weight=1)

    def create_widgets(self):
        """Layout the elements on screen."""

        self.box = tk.Text(self)
        self.box.grid(row=0,
                      column=0,
                      rowspan=50,
                      columnspan=24,
                      sticky='news')

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        """Set the text to be displayed in the window."""
        self._text = str(value)

    def update(self):
        """Update the displayed contents of the window."""
        self.text = fetch()

        self.box['state'] = tk.NORMAL
        self.box.delete(1.0, tk.END)

        for line in self._text.splitlines():
            self.box.insert(tk.END, line + "\n")

        # Move the cursor to the end to prevent the display from jumping
        # back to the beginning after each refresh.
        self.box.see(tk.END)

        self.box['state'] = tk.DISABLED

    def poll(self):
        """Update the UI on each polling interval."""
        self.update()
        self.after(self.polling_interval_ms, self.poll)
