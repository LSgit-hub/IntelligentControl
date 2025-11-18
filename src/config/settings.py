#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 默认配置
DEFAULT_CONFIG = {
    "ai": {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": "",
        "base_url": "",
        "temperature": 0.7,
        "max_tokens": 1500
    },
    "mcp": {
        "enabled": False,
        "host": "localhost",
        "port": 8000
    },
    "tools": {
        "timeout": 30,
        "allowed_commands": [],
        "blocked_commands": ["rm -rf /", "del /f /s /q"]
    },
    "ui": {
        "theme": "default",
        "history_size": 100
    }
}

def load_settings(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件

    参数:
        config_path: 配置文件路径，如果为None则使用默认路径

    返回:
        配置字典
    """
    # 确定配置文件路径
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config.json")

    # 创建默认配置
    config = DEFAULT_CONFIG.copy()

    # 从环境变量加载配置
    _load_from_env(config)

    # 从配置文件加载配置
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                _merge_config(config, file_config)
        except Exception as e:
            print(f"警告: 无法加载配置文件 {config_path}: {str(e)}")

    return config

def _load_from_env(config: Dict[str, Any]) -> None:
    """从环境变量加载配置"""
    # AI配置
    if "OPENAI_API_KEY" in os.environ:
        config["ai"]["api_key"] = os.environ["OPENAI_API_KEY"]
    if "OPENAI_BASE_URL" in os.environ:
        config["ai"]["base_url"] = os.environ["OPENAI_BASE_URL"]
    if "AI_MODEL" in os.environ:
        config["ai"]["model"] = os.environ["AI_MODEL"]
    if "AI_TEMPERATURE" in os.environ:
        try:
            config["ai"]["temperature"] = float(os.environ["AI_TEMPERATURE"])
        except ValueError:
            pass

    # MCP配置
    if "MCP_ENABLED" in os.environ:
        config["mcp"]["enabled"] = os.environ["MCP_ENABLED"].lower() == "true"
    if "MCP_HOST" in os.environ:
        config["mcp"]["host"] = os.environ["MCP_HOST"]
    if "MCP_PORT" in os.environ:
        try:
            config["mcp"]["port"] = int(os.environ["MCP_PORT"])
        except ValueError:
            pass

def _merge_config(base_config: Dict[str, Any], new_config: Dict[str, Any]) -> None:
    """
    递归合并配置

    参数:
        base_config: 基础配置
        new_config: 新配置
    """
    for key, value in new_config.items():
        if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
            _merge_config(base_config[key], value)
        else:
            base_config[key] = value

def save_settings(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    保存配置到文件

    参数:
        config: 配置字典
        config_path: 配置文件路径，如果为None则使用默认路径
    """
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config.json")

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"错误: 无法保存配置文件 {config_path}: {str(e)}")
