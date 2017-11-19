
import os, sys

import logging
import logging.config

def setup():
    logging.config.fileConfig(os.path.join(os.path.dirname(__file__),
        "logging.conf"))

