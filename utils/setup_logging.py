import logging
import sys
import os
import pathlib
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict
from colorama import Fore, Back, Style

DEFAULT_STREAM_LOG_LEVEL = logging.INFO
DEFAULT_FILE_LOG_LEVEL = logging.DEBUG


# Ref: https://gist.github.com/joshbode/58fac7ababc700f51e2a9ecdebe563ad
class ColoredFormatter(logging.Formatter):
    """Colored log formatter."""

    def __init__(
        self, *args, colors: Optional[Dict[str, str]] = None, **kwargs
    ) -> None:
        """Initialize the formatter with specified format strings."""

        super().__init__(*args, **kwargs)

        self.colors = colors if colors else {}

    def format(self, record) -> str:
        """Format the specified record as text."""

        record.color = self.colors.get(record.levelname, "")
        record.reset = Style.RESET_ALL

        return super().format(record)


def setup_logging(
    file_name,
    stream_log_level=DEFAULT_STREAM_LOG_LEVEL,
    file_log_level=DEFAULT_FILE_LOG_LEVEL,
):
    logger = logging.getLogger(file_name)
    logger.setLevel(logging.DEBUG)

    # Stream Handler
    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setLevel(stream_log_level)
    stream_formatter = ColoredFormatter(
        "{asctime} |{color} {levelname:8} {reset}|: {message}",
        style="{",
        colors={
            "DEBUG": Fore.CYAN,
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
        },
        # uncomment to revert to default time format
        datefmt="%H:%M:%S",
    )
    stream_handler.setFormatter(stream_formatter)

    # uncomment lines to log to a file
    # File Handler
    # log_file_path = os.path.join(
    #     str(pathlib.Path(os.path.abspath(__file__)).parent), "logs", file_name
    # )
    # file_handler = RotatingFileHandler(
    #     filename=log_file_path, maxBytes=100000, backupCount=10
    # )

    # fmt = "%(asctime)s | %(threadName)-12s | [%(levelname)-8s] | %(funcName)-20s|: %(message)s"
    # datefmt = "%Y-%m-%d %H:%M:%S"
    # formatter = logging.Formatter(fmt, datefmt)

    # file_handler.setFormatter(formatter)
    # file_handler.setLevel(file_log_level)

    # logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
