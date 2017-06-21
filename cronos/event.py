# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

_callbacks = set()

def register(fn):
    _callbacks.add(fn)

def notify():
    for cb in _callbacks:
        cb()
