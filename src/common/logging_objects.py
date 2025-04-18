import re
import os
import yaml
import logging
import time
from logging import handlers
from typing import Any


# noinspection PyTypeChecker
class TimedAndSizeRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    FileHandler that can rotate by both time and size.
    """

    def __init__(self, filename: str, mode: str = 'a', maxBytes: int = 0, backupCount: int = 0, encoding: str = None,
                 delay: bool = False, when: str = 'h', interval: int = 1, utc: bool = False) -> None:
        """
        Inits TimedAndSizeRotatingFileHandler.
        :param filename: Name for created log files.
        :param mode: Mode of opening the log file.
        :param maxBytes: Maximum number of bytes after which the file is rotated.
        :param backupCount: Maximum number of files kept.
        :param encoding: Encoding of the log file.
        :param delay: Delay opening the file until first write.
        :param when: When timed rollover occurs.
        :param interval: Multiplies the when parameter.
        :param utc: Use UTC.
        """
        filename = f'{filename}.{time.strftime("%Y-%m-%d", time.localtime())}.log'
        logging.handlers.TimedRotatingFileHandler.__init__(self, filename=filename, when=when, interval=interval,
                                                           backupCount=backupCount, encoding=encoding, delay=delay,
                                                           utc=utc)
        logging.handlers.RotatingFileHandler.__init__(self, filename=filename, mode=mode, maxBytes=maxBytes,
                                                      backupCount=backupCount, encoding=encoding, delay=delay)
        self.namer = lambda name: f'{name}.log'

    def computeRollover(self, current_time):
        return logging.handlers.TimedRotatingFileHandler.computeRollover(self, current_time)

    def doRollover(self):
        # get from logging.handlers.TimedRotatingFileHandler.doRollover()
        current_time = int(time.time())
        dst_now = time.localtime(current_time)[-1]
        new_rollover_at = self.computeRollover(current_time)

        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dst_at_rollover = time.localtime(new_rollover_at)[-1]
            if dst_now != dst_at_rollover:
                if not dst_now:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                new_rollover_at += addend
        self.rolloverAt = new_rollover_at

        return logging.handlers.RotatingFileHandler.doRollover(self)

    def shouldRollover(self, record):
        return logging.handlers.TimedRotatingFileHandler.shouldRollover(self, record) or \
            logging.handlers.RotatingFileHandler.shouldRollover(self, record)


def parse_config(path: str = None, data: str = None, tag:str = '!ENV') -> Any:
    """
    Loads a yaml configuration file and resolve any environment variables.
    The environment variables must have !ENV before them and be in this format
    to be parsed: ${VAR_NAME}.
    E.g.:
    database:
        host: !ENV ${HOST}
        port: !ENV ${PORT}
    app:
        log_path: !ENV '/var/${LOG_PATH}'
        something_else: !ENV '${AWESOME_ENV_VAR}/var/${A_SECOND_AWESOME_VAR}'
    :param path: The path to the yaml file.
    :param data: The yaml data itself as a stream.
    :param tag: The tag to look for.
    :return: The dict configuration.
    """
    # pattern for global vars: look for ${word}
    pattern = re.compile('.*?\${(\w+)}.*?')
    loader = yaml.SafeLoader

    # the tag will be used to mark where to start searching for the pattern
    # e.g. somekey: !ENV somestring${MYENVVAR}blah blah blah
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables_str(loader, node) -> str:
        """
        Extracts the environment variable from the node's value, possibly adding default value if none exists.
        :param yaml.Loader loader: the yaml loader.
        :param node: The current node in the yaml.
        :return: The parsed string that contains the value of the environment variable.
        """
        value = loader.construct_scalar(node)
        DEFAULTS = {'HOSTNAME': 'DEFAULT'}
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(
                    f'${{{g}}}', os.getenv(g, DEFAULTS[g])
                )
            return full_value
        return value

    def constructor_env_variables_list(loader, node) -> str:
        """
        Extracts the environment variable from the node's value, possibly adding default value if none exists.
        :param yaml.Loader loader: The yaml loader.
        :param node: The current node in the yaml.
        :return: The parsed list that contains the value of the environment variable.
        """
        value = loader.construct_scalar(node)
        DEFAULTS = {'LOGGING_HANDLERS': 'std_output'}
        match = pattern.findall(value)
        if match[0]:
            return os.getenv(match[0], DEFAULTS[match[0]]).split(',')
        return value

    def constructor_env_variables(loader, node) -> str:
        """
        Extracts the environment variable from the node's value, possibly adding default value if none exists.
        :param yaml.Loader loader: The yaml loader.
        :param node: The current node in the yaml.
        :return: The parsed value that contains the value of the environment variable.
        """
        value = loader.construct_scalar(node)
        DEFAULTS = {'LOGGING_LEVEL': 'DEBUG'}
        match = pattern.findall(value)
        if match[0]:
            return os.getenv(match[0], DEFAULTS[match[0]])
        return value

    loader.add_constructor('!ENVSTR', constructor_env_variables_str)
    loader.add_constructor('!ENVLST', constructor_env_variables_list)
    loader.add_constructor('!ENV', constructor_env_variables)

    if path:
        with open(path) as conf_data:
            return yaml.load(conf_data, Loader=loader)
    elif data:
        return yaml.load(data, Loader=loader)
    else:
        raise ValueError('Either a path or data should be defined as input')
