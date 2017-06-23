# Copyright (C) 2017, Anthony Oteri
# All rights reserved

from __future__ import absolute_import

import collections
import dataset
import logging
import time
from datetime import datetime, timedelta

from sqlalchemy.sql import and_

from cronos.utils import timestamp


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

    def ongoing(self):
        with conn as tx:
            last = tx['record'].find_one(elapsed=0, order_by='-start')
            return last

    def by_day(self, start_date=None, stop_date=None):
        with conn as tx:
            min_ts = timestamp(start_date) if start_date is not None else 0
            max_ts = timestamp(stop_date) if stop_date is not None else 0

            data = collections.defaultdict(list)
            t = tx['record']
            try:
                if min_ts and max_ts:
                    rows = t.find(
                        and_(t.table.columns.start >= min_ts,
                             t.table.columns.start <= max_ts))
                elif min_ts:
                    rows = t.find(t.table.columns.start >= min_ts)
                elif max_ts:
                    rows = t.find(t.table.colunms.start <= max_ts)
                else:
                    rows = t.all()

            except AttributeError:
                rows = []

            for row in rows:
                try:
                    ts = datetime.utcfromtimestamp(float(row['start']))
                except TypeError:
                    continue
                now = int(time.time())

                if stop_date:
                    if ts > stop_date:
                        raise Exception("Bad timestamp %s > %s" % (
                            ts.isoformat(), stop_date.isoformat()))

                data[ts.date().isoformat()].append({
                    'project': row['project'],
                    'start_ts': row['start'],
                    'stop_ts': row['start'] + row['elapsed'],
                    'elapsed': row['elapsed'],
                })

            return data

def insert_fake_records():

    projects = ('foo', 'bar', 'baz', 'boom', 'hannah', 'luke')
    project_service = ProjectService()

    for project in projects:
        project_service.create(name=project)

    min_ts = timestamp(datetime.now()) - timedelta(weeks=12).total_seconds()
    max_ts = timestamp(datetime.now()) + timedelta(weeks=12).total_seconds()

    record_service = RecordService()

    import random
    for _ in xrange(2000):
        start = random.randint(min_ts, max_ts)
        duration = random.randint(1, 3 * 60 * 60)
        project = random.choice(projects)
        record_service.start(project, start)
        record_service.stop(project, start, start + duration)


