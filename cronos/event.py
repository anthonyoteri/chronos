# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

from functools import wraps

_callbacks = set()


def notify(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        for cb in _callbacks:
            cb()
        return result

    return wrapper


@notify
def register(fn):
    _callbacks.add(fn)
