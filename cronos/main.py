# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

from __future__ import absolute_import

import argparse
import json
import logging

import yaml

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
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loglevel', help='Logging level',
                        default='info', choices=['debug', 'info', 'warning',
                                                 'error'])
    parser.add_argument('-c', '--config', help='Config file',
                        default='~/.cronos/config.yml')

    options = parser.parse_args()
    cronos.logging.init(level=_log_level(options.loglevel))

    try:
        with open(options.config, 'r') as config_file:
            config = yaml.load(config_file)
        log.debug(json.dumps(config, indent=2))
    except IOError as e:
        log.error("Unable to read configuration file %s: %s", options.config, e)
        raise e

    connect(config)

    # TODO: Remove me
#    from cronos.db import insert_fake_records
#    insert_fake_records()

    app = Application()
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit(0)

