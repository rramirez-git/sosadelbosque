import os
from datetime import datetime

from sosadelbosque.settings import BASE_DIR

class CLogger():

    logfile = os.path.join(BASE_DIR, 'logs/log_{}.log'.format(
        datetime.now().strftime("%Y_%m_%d")))

    def write(self, message):
        with open(self.logfile, "a") as log:
            log.write("{}: {}\n".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                message
            ))


Logger = CLogger()
