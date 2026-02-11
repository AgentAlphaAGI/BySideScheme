import logging
import os
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name: str = "BySideScheme", log_level: int = logging.INFO):
    """
    配置并返回一个 logger 实例
    - 同时输出到控制台和文件
    - 文件日志支持自动轮转 (RotatingFileHandler)
    """
    # 获取日志目录
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, "app.log")

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s'
    )

    # 1. 控制台 Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 文件 Handler (按大小轮转，最大 5MB，保留 3 个备份)
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# 创建全局 logger 实例
logger = setup_logger()
