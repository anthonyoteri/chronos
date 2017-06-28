# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Helper utility functions."""

from __future__ import absolute_import, division

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO, SU
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


def midnight(dt):
    """Return a datetime representing midnight of the given datetime.

    :param date|datetime dt: A date or datetime object as the reference.
    :return datetime:
    """

    if isinstance(dt, datetime):
        dt = dt.date()

    return datetime.combine(dt, datetime.min.time())


def last_second(dt):
    """Return a datetime representing the final second of the day."""

    midnight_today = midnight(dt)
    midnight_tomorrow = midnight(midnight_today + timedelta(days=1))
    return midnight_tomorrow - timedelta(seconds=1)


def start_of_day(dt):
    """Return the first second in the day."""
    return midnight(dt)


def end_of_day(dt):
    """Return the last second in the day."""
    return last_second(dt)


def start_of_month(dt):
    """Return the first second of the first day of the month."""
    return midnight(dt.replace(day=1))


def end_of_month(dt):
    """Return the last second of the final day of the month."""
    first_of_this_month = start_of_month(dt)
    first_of_next_month = start_of_month(first_of_this_month + relativedelta(
        months=1))
    last_of_this_month = first_of_next_month - timedelta(days=1)

    return last_second(last_of_this_month)


def start_of_week(dt):
    """Return the first second of the Monday of the given week."""
    monday = dt - relativedelta(weekday=MO(-1))
    return midnight(monday)


def end_of_week(dt):
    """Return the last second of the Sunday of the given week."""
    sunday = dt + relativedelta(weekday=SU)
    return last_second(sunday)
