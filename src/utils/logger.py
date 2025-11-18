#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志工具模块
"""

import os
import sys
import logging
from loguru import logger
from pathlib import Path

def setup_logger(name, level="INFO"):
    """
    设置日志记录器

    参数:
        name: 日志记录器名称
        level: 日志级别

    返回:
        日志记录器实例
    """
    # 确保日志目录存在
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>: <level>{message}</level>",
        level=level,
        colorize=True
    )

    # 添加文件输出
    logger.add(
        log_dir / f"{name}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}: {message}",
        level=level,
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )

    return logger
