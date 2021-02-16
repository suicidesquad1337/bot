import logging
from contextlib import contextmanager
from pathlib import Path

import colorlog

from .utils.config import BOT_CONFIG

LOG_DIR = Path(__file__).parent.parent / "logs"

STYLE = "{"
LOG_FORMAT = "[{levelname}] {asctime} - {name}:{lineno} {message}"
LOG_FORMAT_COLORED = "{log_color}[{levelname}] {asctime} - {name}:{lineno} {message}"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


@contextmanager
def log(stream: bool = False):
    LOG_DIR.mkdir(exist_ok=True)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("chardet").setLevel(logging.WARNING)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if BOT_CONFIG.debug_mode else logging.INFO)

    file_handler = logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FMT, STYLE))
    logger.addHandler(file_handler)

    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            colorlog.ColoredFormatter(LOG_FORMAT_COLORED, DATE_FMT, STYLE)
        )
        logger.addHandler(stream_handler)

    try:
        yield
    finally:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
