# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Main script for chronos timekeeper."""

from __future__ import absolute_import

import argparse
import logging

from chronos import config
import chronos.logging

from chronos.application import Application
from chronos.db import connect

log = logging.getLogger('chronos')


def _log_level(level):
    return {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
    }[level]


def main():
    """"Main entrypoint."""

    parser = argparse.ArgumentParser()
    parser.add_argument('-l',
                        '--loglevel',
                        help='Logging level',
                        default='info',
                        choices=['debug', 'info', 'warning', 'error'])
    parser.add_argument('-c',
                        '--config',
                        help='Config file',
                        default='~/.chronos/config.yml')

    options = parser.parse_args()
    chronos.logging.init(level=_log_level(options.loglevel))

    import os
    log.error("Path is %s", os.path.dirname(os.path.realpath(__file__)))

    config.load(options.config)
    connect()

    app = Application()
    app.run()

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(0)
