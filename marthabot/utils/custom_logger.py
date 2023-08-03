import logging
import sys
import os
import pathlib
import textwrap
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict
from colorama import Fore, Back, Style


from marthabot.configurations import log_config as config

    

class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        wrapper = textwrap.TextWrapper(
            initial_indent=' '*config.OVERFLOW_INDENT,
            width=config.OVERFLOW_WIDTH,
            subsequent_indent=' '*config.OVERFLOW_INDENT,
        )

        overflow =  self.args.get("overflow","") if isinstance(self.args,dict) else ""
        lines = overflow.split("\n")
        if lines[-1] == "":
            lines.pop()
        lines = [wrapper.fill(l) for l in lines]
        self.overflow = "\n" + "\n".join(lines) if lines else ""

class CustomLogger(logging.Logger):
    def __init__(self,name: str=os.path.basename(__file__),stream_log_level=config.DEFAULT_STREAM_LOG_LEVEL) -> None:
        super().__init__(name)
        if name in logging.root.manager.loggerDict:
            print(name,"already exists")

        else:
            self.wrapper = textwrap.TextWrapper(initial_indent=' '*config.OVERFLOW_INDENT, width=config.OVERFLOW_WIDTH,
                               subsequent_indent=' '*config.OVERFLOW_INDENT)
            # Stream Handler
            stream_handler = StreamHandler(sys.stdout)
            stream_handler.setLevel(stream_log_level)
            # TODO consider which parts of message should be colored
            format = (
                "|%(color)s"       
                "[%(asctime)s%(msecs)03d]" 
                "%(levelname)-8s|"
                f"[Thread: %(threadName){config.THREAD_NAME_LENGTH}s]" 
                # f"%(funcName){config.FUNC_NAME_LENGTH}s in " 
                "[%(filename)s:%(lineno)d]" 
                " %(message)s" 
                "%(reset)s" 
                "%(overflow)s" 
            )
            if config.LOGGER_NAMES_ENABLE:
                format += "\n|--- Logged by logger: %(name)s"
            if config.FUNC_NAME_ENABLE:
                format += "\n|--- Called in function: %(funcName)s"

            stream_formatter = ColoredFormatter(
                format,
                colors={
                    "DEBUG": Fore.CYAN,
                    "INFO": Fore.GREEN,
                    "WARNING": Fore.YELLOW,
                    "ERROR": Fore.RED,
                    "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
                },
                datefmt="%H:%M:%S.",
            )

            stream_handler.setFormatter(stream_formatter)
            if (self.hasHandlers()):
                self.handlers.clear()
            self.addHandler(stream_handler)
            self.setLevel(logging.DEBUG)

    # TODO These overrides only work in python 3.8 (currently project is using 3.7)
    # def info(self, msg,stacklevel=2, overflow = "", *args, **kwargs):
    #     if overflow:
    #         overflow = "\n" + self.wrapper.fill(overflow)
    #     return super(CustomLogger, self).info(msg,extra={"overflow":overflow})
    # def warning(self, msg, stacklevel=2,overflow = "", *args, **kwargs):
    #     if overflow:
    #         overflow = "\n" + self.wrapper.fill(overflow)
    #     return super(CustomLogger, self).warning(msg,extra={"overflow":overflow})
    # def error(self, msg, stacklevel=2,overflow = "", *args, **kwargs):
    #     if overflow:
    #         overflow = "\n" + self.wrapper.fill(overflow)
    #     return super(CustomLogger, self).error(msg,extra={"overflow":overflow})
    # def debug(self, msg, stacklevel=2,overflow = "", *args, **kwargs):
    #     if overflow:
    #         overflow = "\n" + self.wrapper.fill(overflow)
    #     return super(CustomLogger, self).debug(msg,stacklevel=2,extra={"overflow":overflow})

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



def setup_logging(name="marthabot"):
    logging.setLoggerClass(CustomLogger)
    logging.setLogRecordFactory(CustomLogRecord)
    return logging.getLogger(name)
    

