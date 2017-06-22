# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import logging
import time
import Tkinter as tk
import ttk

from cronos import event
from cronos.utils import human_time


log = logging.getLogger(__name__)


class Console(ttk.Frame, object):
    POLLING_INTERVAL_MS = 250

    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        for row in xrange(40):
            self.rowconfigure(row, weight=1)
        for col in xrange(24):
            self.rowconfigure(col, weight=1)

        self._text = ''
        self.polling_interval_ms = Console.POLLING_INTERVAL_MS

        self.create_widgets()
        self._poll()

    def create_widgets(self):
        self.box = tk.Text(self)
        self.box.grid(row=0, column=0, rowspan=40, columnspan=24,
                      sticky='news')

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)

    def _update(self):
        self.box['state'] = tk.NORMAL
        self.box.delete(1.0, tk.END)

        for line in self._text.splitlines():
            self.box.insert(tk.END, line + "\n")

        self.box.see(tk.END)

        self.box['state'] = tk.DISABLED

    def _poll(self):
        self.poll()
        self.after(self.polling_interval_ms, self._poll)

    def poll(self):
        pass
