import logging
import os
from datetime import datetime

from sosadelbosque.settings import BASE_DIR

class CLogger():

    def __init__(self):
        logfile = os.path.join(BASE_DIR, 'logs/log_{}.log'.format(
            datetime.now().strftime("%Y_%m_%d")))
        with open(logfile, "a"):
            pass
        logging.basicConfig(
            level=logging.INFO,
            filename=logfile,
            format="%(asctime)s: %(message)s"
        )

    def write(self, message):
        logging.info(message)

    def exception(self, message):
        logging.info(message, exc_info=True)


Logger = CLogger()
