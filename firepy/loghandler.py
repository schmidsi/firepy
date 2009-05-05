import logging
from firepy.firephp import FirePHP


class FirePHPHandler(logging.Handler):
    logs = []

    def emit(self, record):
        """
        Record all the logs that comes by converting them to JSON notation.
        """
        if record.exc_info:
            FirePHPHandler.logs.append(FirePHP.exception(record))
        else:
            FirePHPHandler.logs.append(FirePHP.log(record))
