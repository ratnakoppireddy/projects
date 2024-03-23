import logging
import logging.handlers

LOG_FILENAME = 'paylater.log'
FORMAT = '%(levelname)7s%(name)10s%(filename)15s:%(lineno)4d -%(funcName)8s %(asctime)s, %(msecs)s, %(message)s'

logging.basicConfig(
            filename = LOG_FILENAME,
            filemode = 'a',
            level = logging.INFO,
            format = FORMAT,
            datefmt = '%H:%M:%S')

logger = logging.getLogger('abcLogger')
# Adding Console handler

fhandler = logging.handlers.RotatingFileHandler(
       LOG_FILENAME, maxBytes=100, backupCount=3)

logger.addHandler(fhandler)