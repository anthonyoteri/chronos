# Copyright (C) 2017, Anthony Oteri
# All rights reserved.

import argparse
import json
import logging

import yaml

from cronos.application import Application


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
    logging.basicConfig(level=_log_level(options.loglevel))

    try:
        with open(options.config, 'r') as config_file:
            config = yaml.load(config_file)
        log.debug(json.dumps(config, indent=2))
    except IOError as e:
        log.error("Unable to read configuration file %s: %s", options.config, e)
        raise e

    app = Application()
    app.run()


if __name__ == "__main__":
    main()

