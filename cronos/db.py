# Copyright (C) 2017, Anthony Oteri
# All rights reserved

from __future__ import absolute_import

import logging

import dataset


log = logging.getLogger(__name__)

_db = None


def connect(config=None):
    log.debug("connect")

    if config:
        db_url = config.get('database', {}).get('url', 'sqlite://')
    else:
        db_url = 'sqlite://'

    log.debug("found database url %s", db_url)

    global _db
    _db = dataset.connect(db_url)

    log.debug("db is %r", _db)

    return _db


class ProjectDao(object):

    def __init__(self):
        assert _db is not None
        self.db = _db

    def create(self, **project):
        log.debug("create: %s", project)

        with self.db as tx:
            tx['project'].insert(project)

    def list(self):
        with self.db as tx:
            return tx['project'].all()

    def get(self, **filter):
        with self.db as tx:
            return tx['project'].find(**filter)

    def delete(self, **filter):
        with self.db as tx:
            tx['project'].delete(**filter)
