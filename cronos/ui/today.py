# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import logging
import time
import Tkinter as tk

from cronos import event
from cronos.db import RecordService
from cronos.ui.console import Console
from cronos.utils import human_time


log = logging.getLogger(__name__)


class Today(Console):

    def __init__(self, master):
        super(Today, self).__init__(master)
        self.data = {}

        self.record_service = RecordService()

        event.register(self.update)

    def load(self):
        log.debug("load: %r", self)
        self.data = {
            'foo': 9999,
            'bar': 12000,
            'baz': 900,
            'bam': 123,
        }

    def update(self):
        log.debug("update: %r", self)
        self.load()
        self.text = ""
        for k, v in sorted(self.data.iteritems()):
            self.text += "%s: %s\n" % (k, human_time(v))

        self.text = "\n".join([str(x) for x in self.record_service.list()])

        self._update()
