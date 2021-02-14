import logging
from contextlib import contextmanager
from pathlib import Path

import colorlog

LOG_DIR = Path(__file__).parent.parent / "logs"

STYLE = "{"
LOG_FORMAT = "{log_color}[{levelname}] {asctime} - {name}:{lineno} {message}"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


@contextmanager
def log(stream: bool = False):
    LOG_DIR.mkdir(exist_ok=True)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("chardet").setLevel(logging.WARNING)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FMT, STYLE))
    logger.addHandler(file_handler)

    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            colorlog.ColoredFormatter(LOG_FORMAT, DATE_FMT, STYLE)
        )
        logger.addHandler(stream_handler)

    try:
        yield
    finally:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
