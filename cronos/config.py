# Copyright (C) 2017, Anthony Oteri
# All rights reserved.
"""Module for holding onto the configuration."""

from __future__ import absolute_import

import logging
import json
import yaml

log = logging.getLogger(__name__)

config = {}


def load(filename, dump=None):
    """Load the configuration from the given filename.

    If `dump` is truthful, dump the config to the logfile.
    """
    global config
    try:
        with open(filename, 'r') as config_file:
            config = yaml.load(config_file)
        if dump:
            log.debug(json.dumps(config, indent=2))

    except IOError as e:
        log.error("Error reading configuration file %s: %s", filename, e)


def get(key, *default):
    """Get a value from the configuration."""

    return config.get(key, *default)


def database(key, *default):
    """Get a value from the database config."""
    db_config = get('database', {})
    return db_config.get(key, *default)


def ui(key, *default):
    """Get a value from the UI config."""
    ui_config = get('ui', {})
    return ui_config.get(key, *default)

