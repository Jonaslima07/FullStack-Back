import logging
from logging.handlers import RotatingFileHandler

# Create a logger
logger = logging.getLogger('log_level_change')

# Configure logger to log messages of DEBUG level and above
logger.setLevel(logging.INFO)

# Define a StreamHandler to log messages to the console
streamHandler = logging.StreamHandler()
logger.addHandler(streamHandler)

fileHandler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
logger.addHandler(fileHandler)

# Log messages at different levels
logger.debug('This is a debug message')    # Shown
logger.info('This is an info message')      # Shown
logger.warning('This is a warning message')  # Shown
logger.error('This is an error message')    # Shown
logger.critical('This is a critical message')  # Shown