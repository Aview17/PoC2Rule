"""日志模块。"""

import logging
import sys
from pathlib import Path


def setup_logger(config: dict) -> logging.Logger:
    """初始化日志系统。"""
    log_config = config.get("logging", {})
    level_str = log_config.get("level", "INFO")
    fmt = log_config.get(
        "format",
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    log_file = log_config.get("file", "./logs/app.log")

    level = getattr(logging, level_str.upper(), logging.INFO)

    logger = logging.getLogger("poc2rule")
    logger.setLevel(level)

    # 防止重复添加 handler
    if logger.handlers:
        return logger

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(fmt)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件 handler
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(fmt)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger
