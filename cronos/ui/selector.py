# Copyright (C) 2017, Anthony Oteri
# All rights reserved

import logging
import Tkinter as tk


log = logging.getLogger(__name__)


class Selector(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.create_widgets()

    def create_widgets(self):
        self.label = tk.LabelFrame(self, text="Select Project")
        self.label['padx'] = 5
        self.label['pady'] = 5
        self.label.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        self.box = tk.Listbox(self.label)
        self.box['selectmode'] = tk.SINGLE
        self.box['relief'] = tk.FLAT
        self.box.pack(fill=tk.BOTH, expand=1)

