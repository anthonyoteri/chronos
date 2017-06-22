# Copyright (C) 2017, Anthony Oteri
# All rights reserved

from __future__ import absolute_import

import collections
import logging
import time

from datetime import datetime, timedelta

import dataset


log = logging.getLogger(__name__)

conn = None


def connect(config=None):
    log.debug("connect")

    if config:
        db_url = config.get('database', {}).get('url', 'sqlite://')
    else:
        db_url = 'sqlite://'

    log.debug("found database url %s", db_url)

    global conn
    conn = dataset.connect(db_url)

    log.debug("db is %r", conn)

    return conn



class ProjectService(object):

    def create(self, name):
        log.debug("create: %s", name)

        with conn as tx:
            tx['project'].insert({'name': name})

    def list(self):
        with conn as tx:
            return tx['project'].all()

    def delete(self, **filter):
        with conn as tx:
            tx['project'].delete(**filter)


class RecordService(object):

    def start(self, project, ts):
        log.debug("start: project=%s timestamp=%s", project, ts)

        with conn as tx:
            tx['record'].insert(dict(project=project, start=ts, elapsed=0))

    def stop(self, project, start_ts, stop_ts):
        log.debug("stop: project=%s start_ts=%s stop_ts=%s", project, start_ts,
                  stop_ts)

        with conn as tx:
            tx['record'].update(
                dict(project=project, start=start_ts,
                     elapsed=stop_ts - start_ts), ['project', 'start'])

    def list(self):
        with conn as tx:
            return tx['record'].all()

    def by_day(self):
        with conn as tx:

            data = collections.defaultdict(list)
            for row in tx['record'].all():
                ts = datetime.fromtimestamp(row['start'])
                now = int(time.time())
                elapsed_time = row['elapsed'] or now - row['start']
                data[ts.date().isoformat()].append({
                    'project': row['project'],
                    'start_ts': row['start'],
                    'stop_ts': row['start'] + elapsed_time,
                    'elapsed': elapsed_time,
                })

            return data


