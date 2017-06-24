# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Helper utility functions."""

from __future__ import absolute_import, division

from datetime import datetime, timedelta
from dateutil import tz


def human_time(t, round_min=15):
    """Format a timestamp as a human readable string.

    :param int round_min: Round the output to this many minutes,
                          if set to 0, no rounding will occur.
    :return str: A string in the formation HH:MM.
    """

    def td_to_hm(td):
        s = td.total_seconds()
        h = s // 3600
        m = (s % 3600) // 60

        return h, m

    t = int(t)

    r = round_min * 60

    try:
        t = (((int(t) + r / 2) // r) * r)
    except ZeroDivisionError:
        pass

    h, m = td_to_hm(timedelta(seconds=t))
    return "%02d:%02d" % (h, m)


def timestamp(dt):
    """Return the epoch seconds since Jan 1, 1970 UTC.

    :return int: The unix timestamp in UTC.
    """
    return int((dt - datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds())


def local_time(dt):
    """Return a date or datetime in the local timzeone."""
    return dt.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())


def utc_time(dt):
    """Return a date or datetime in utc."""
    return dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())
