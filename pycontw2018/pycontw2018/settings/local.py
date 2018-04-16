from .base import *
import sys
import logging.config

# SECURTY WARNING: don't run with debug truned on in prodcution
DEBUG = True

INTENAL_IPS = ['127.0.0.1']

# Turn of debug while imported by Celery with a workaroubd
if 'celery' in sys.argv[0]:
    DEBUG = False
