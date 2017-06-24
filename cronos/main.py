# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Main script for cronos timekeeper."""

from __future__ import absolute_import

import argparse
import json
import logging

import yaml

from cronos import config
import cronos.logging

from cronos.application import Application
from cronos.db import connect

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
                        default='config.yml')

    options = parser.parse_args()
    cronos.logging.init(level=_log_level(options.loglevel))

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
