# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Global event handler."""

from __future__ import absolute_import

from functools import wraps

_callbacks = set()


def notify(fn):
    """After executing the supplied function, notify all callbacks."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        for cb in _callbacks:
            cb()
        return result

    return wrapper


def register(fn):
    """Register a callable to be notified."""
    _callbacks.add(fn)


@notify
def trigger():
    pass
