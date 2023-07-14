import logging


DEFAULT_STREAM_LOG_LEVEL = logging.DEBUG
DEFAULT_FILE_LOG_LEVEL = logging.DEBUG

THREAD_NAME_LENGTH = 12
FUNC_NAME_LENGTH = 8

#overflow formatting
OVERFLOW_INDENT = 10
OVERFLOW_WIDTH = 80

# Logging
ENABLE_FILE_LOGGING = False
LOG_FILENAME = "~/hsi.log"  # Always in home directory
LOGGING_LEVEL = logging.DEBUG  # For detailed logs change this to 'logging.DEBUG'

LOGGER_NAMES_ENABLE = True

STACK_TRACE_ENABLE = False
FUNC_NAME_ENABLE = False