# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import, division

from datetime import datetime, timedelta


def human_time(t, round_min=15):
    """Format a timestamp as a human readable string."""

    def td_to_hm(td):
        s = td.total_seconds()
        h = s // 3600
        m = (s % 3600) // 60

        return h, m

    t = int(t)

    r = round_min * 60

    try:
        t = (((int(t) + r/2) // r) * r)
    except ZeroDivisionError:
        pass

    h, m = td_to_hm(timedelta(seconds=t))
    return "%02d:%02d" % (h, m)



def timestamp(dt):
    """Return the epoch seconds since Jan 1, 1970 UTC."""
    return int((dt - datetime(1970, 1, 1)).total_seconds())
