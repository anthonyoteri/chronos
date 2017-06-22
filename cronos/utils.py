# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import, division

from datetime import timedelta


def human_time(t, round=15 * 60):
    """Format a timestamp as a human readable string."""

    t = int(t)

    try:
        t = (((int(t) + round/2) // round) * round)
    except ZeroDivisionError:
        pass

    return str(timedelta(seconds=t))


