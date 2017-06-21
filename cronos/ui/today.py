# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

import logging
import time
import Tkinter as tk

from cronos.utils import human_time


log = logging.getLogger(__name__)


class Today(tk.Frame):

    TITLE = "Today"
    POLLING_INTERVAL_MS = 250

    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self._data = {}

        self.create_widgets()
        self.update()
        self.poll()

    def create_widgets(self):

        self.label = tk.LabelFrame(self, text=Today.TITLE)
        self.label['padx'] = 5
        self.label['pady'] = 5
        self.label.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        self.box = tk.Text(self.label)
        self.box.pack(fill=tk.BOTH, expand=1)

    def save(self):
        log.debug("save: %r", self)

    def load(self):
        log.debug("load: %r", self)

        self._data['foo'] = 999
        self._data['foobar'] = 5555
        self._data['Some long baz'] = 2222
        self._data['bam'] = 123

    def update(self):
        log.debug("update: %r", self)
        self.load()

        self.box['state'] = tk.NORMAL
        self.box.delete(1.0, tk.END)

        for k, v in sorted(self._data.iteritems()):
            self.box.insert(tk.END, "%s: %s\n" % (k, human_time(v)))

        self.box['state'] = tk.DISABLED

        self.save()

    def poll(self):
        self.after(Today.POLLING_INTERVAL_MS, self.poll)

