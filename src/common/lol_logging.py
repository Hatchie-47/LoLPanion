import common.logging_objects as logging_objects
import os
import logging.config

"""
This file just loads logging configuration from .yml file, import this at every service main.py file.
"""

configuration = logging_objects.parse_config(path=os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'logging.yml'))
logging.config.dictConfig(configuration)
