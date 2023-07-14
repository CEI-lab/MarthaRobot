import logging
from utils.custom_logger import CustomLogRecord, CustomLogger, setup_logging
# setup_logging()
logging.setLoggerClass(CustomLogger)
logging.setLogRecordFactory(CustomLogRecord)
log = setup_logging()


from marthabot.robot.HSIMaster import HSIMaster

if __name__ == "__main__":
    obj = HSIMaster()
    obj.initializeCommandRegistry()
    obj.startSystem()
