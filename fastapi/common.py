import logging


FORMAT = (
    "%(threadName)s %(levelname)9s %(name)10s%(filename)16s:"
    "%(lineno)4d -%(funcName)5s %(asctime)s, %(msecs)s, %(message)s"
)

# Dev - SIT/INT - QA - UAT - PREPROD - PROD


logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="%H:%M:%S",
    filename="order_mgmt.log",
    filemode="w",
)

log = logging.getLogger("order_mgmt")
