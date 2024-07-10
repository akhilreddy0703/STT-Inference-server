import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Ensure log directory exists
os.makedirs('logs', exist_ok=True)

# Create loggers
main_logger = setup_logger('main_logger', 'logs/main.log')
transcription_logger = setup_logger('transcription_logger', 'logs/transcription.log')
model_logger = setup_logger('model_logger', 'logs/model.log')