import logging
from logging.handlers import RotatingFileHandler

# Create a logger with a unique name
logger = logging.getLogger('example_logger')

# Configure logger to log messages of INFO level and above
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Define a handler to specify where the log messages should be sent
streamHandler = logging.StreamHandler()  # Log messages to console
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Define a RotatingFileHandler to log messages to a rotating set of files
fileHandler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)