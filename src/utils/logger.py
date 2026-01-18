"""
日志系统
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from src.config.settings import (
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_FILE,
    LOG_FILE_MAX_SIZE,
    LOG_FILE_BACKUP_COUNT
)

def setup_logger(name: str, level: str = None) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))

    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=LOG_FILE_MAX_SIZE,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)
