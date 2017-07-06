# Copyright (C) 2017, Anthony Oteri
# All rights reserved
"""Module for handling interaction with the database."""

from __future__ import absolute_import

import collections
import dataset
import logging
from datetime import datetime

from sqlalchemy.sql import and_

from chronos import config
from chronos.utils import timestamp, local_time, utc_time

log = logging.getLogger(__name__)

conn = None


def connect():
    """Initialize the connection with the database.

    :param dict config: The current configuration.
    """
    url = config.get('database', {}).get('url', 'sqlite://')

    global conn
    conn = dataset.connect(url)


class ProjectService(object):
    """Service instance for maintaining the list of projects."""

    def create(self, name):
        """Create a new project with the given name."""

        log.debug("create: %s", name)

        with conn as tx:
            tx['project'].insert({'name': name})

    def list(self):
        """Query for a list of all projects.

        The return value will be a list of `collections.ordereddict`
        objects with the keys "id", and "name".

        :return list<dict>: A list of rows from the database.
        """

        with conn as tx:
            return tx['project'].all()

    def delete(self, **filter):
        """Delete the project by either id or name.

        :param filter: keyword arguments either 'id' or 'name' to narow the
                       list of projects to delete.
        """

        with conn as tx:
            tx['project'].delete(**filter)


class RecordService(object):
    """Service instance for maintaining the actual time records."""

    def start(self, project, ts):
        """Start a new time record.

        :param str project: The name of the project.
        :param int ts: The current epoch seconds (UTC).
        """
        log.debug("start: project=%s timestamp=%s", project, ts)

        with conn as tx:
            tx['record'].insert(dict(project=project, start=ts, elapsed=0))

    def stop(self, project, start_ts, stop_ts):
        """Stop the current time record.

        :param str project: The name of the project.
        :param int start_ts: The epoch seconds (UTC) when the record was
                             started.
        :param int stop_ts: The epoch seconds (UTC) when the record is to be
                            stopped.
        """

        log.debug("stop: project=%s start_ts=%s stop_ts=%s", project, start_ts,
                  stop_ts)

        with conn as tx:
            tx['record'].update(
                dict(project=project,
                     start=start_ts,
                     elapsed=stop_ts - start_ts), ['project', 'start'])

    def list(self):
        """Qurey for a list of all records.

        The return value will be a list of `collections.ordereddict` objects,
        each containing the following fields: id, start, elapsed.

        :return list<dict>: The result set.
        """

        with conn as tx:
            return tx['record'].all()

    def ongoing(self):
        """Query for the last ongoing recording.

        A recording is considered ongoing if the `elapsed` field is set to
        0 seconds.

        :return collections.ordereddict: The last started ongoing row or
                                         `None` if there is no ongoing
                                         records.
        """
        with conn as tx:
            last = tx['record'].find_one(elapsed=0, order_by='-start')
            return last

    def by_day(self, start_date=None, stop_date=None, filter_=None):
        """Query for records grouped by day.

        The result will be a `collections.ordereddict` with one entry per day,
        each day will contain a list of records which were started on that
        day.  The key will be in ISO8601 format for the date, e.g.
        'YYYY-MM-DD'.

        :param datetime start_date: An optional starting date (inclusive)
        :param datetime stop_date: An optional stopping date (inclusive)
        :param str filter_: filter string for projects.
        :return collections.ordereddict.
        """

        start_date = utc_time(start_date) if start_date else None
        stop_date = utc_time(stop_date) if stop_date else None

        with conn as tx:
            min_ts = timestamp(start_date) if start_date is not None else 0
            max_ts = timestamp(stop_date) if stop_date is not None else 0

            data = collections.defaultdict(list)
            t = tx['record']
            try:
                if filter_ and min_ts and max_ts:
                    rows = t.find(and_(t.table.columns.start >= min_ts,
                                       t.table.columns.start <= max_ts,
                                       t.table.columns.project.ilike(filter_ +
                                                                     '%')))
                elif min_ts and max_ts:
                    rows = t.find(and_(t.table.columns.start >= min_ts,
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
                    ts = local_time(datetime.utcfromtimestamp(float(row[
                        'start'])))
                except TypeError:
                    continue

                data[ts.date()].append({
                    'project': row['project'],
                    'start_ts': row['start'],
                    'stop_ts': row['start'] + row['elapsed'],
                    'elapsed': row['elapsed'],
                })

            return data
