"""
日志系统

统一的日志管理，支持多级别日志、文件轮转、彩色终端输出
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }

    def format(self, record):
        # 添加颜色
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        return super().format(record)


class Logger:
    """日志管理器"""

    _instance: Optional[logging.Logger] = None

    @classmethod
    def get_logger(
        cls,
        name: str = "ai-coding",
        level: str = "INFO",
        log_file: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ) -> logging.Logger:
        """
        获取日志实例

        Args:
            name: 日志名称
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: 日志文件路径
            max_bytes: 单个日志文件最大大小
            backup_count: 保留的日志文件数量

        Returns:
            logging.Logger: 日志实例
        """
        if cls._instance is not None:
            return cls._instance

        # 创建logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))

        # 避免重复添加handler
        if logger.handlers:
            cls._instance = logger
            return logger

        # 控制台handler（彩色输出）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # 文件handler（如果指定了日志文件）
        if log_file:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        cls._instance = logger
        return logger

    @classmethod
    def reset(cls):
        """重置日志实例（用于测试）"""
        if cls._instance:
            for handler in cls._instance.handlers[:]:
                handler.close()
                cls._instance.removeHandler(handler)
            cls._instance = None


# 便捷函数
def get_logger(
    name: str = "ai-coding",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """获取日志实例的便捷函数"""
    return Logger.get_logger(name, level, log_file)
