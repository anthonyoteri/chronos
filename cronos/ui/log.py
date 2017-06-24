# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

"""UI element for displaying the current log."""

from __future__ import absolute_import

import logging
import time

from cronos import event
from cronos.logging import fetch
from cronos.ui.console import Console


log = logging.getLogger(__name__)


class Log(Console):
    """UI Widget for displaying the most recent log lines."""

    def __init__(self, master):
        """Initialize the widget."""

        super(Log, self).__init__(master)

        self.polling_interval_ms = 250

        event.register(self.update)

    def update(self):
        """Refresh the contents with the latest."""

        self.text = fetch()

        # Ensure we update the textbox.
        self._update()

    def poll(self):
        """Update the UI on each polling interval."""
        self.update()
