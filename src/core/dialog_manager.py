#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
对话管理模块
负责管理AI对话上下文和历史记录
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DialogManager:
    """对话管理器类"""

    def __init__(self, settings: Dict[str, Any]):
        """
        初始化对话管理器

        参数:
            settings: 配置字典
        """
        self.settings = settings
        self.dialog_history = []
        self.context = {}
        self.max_history = settings.get("ui", {}).get("history_size", 100)
        self.history_file = Path("dialog_history.json")

        # 加载历史对话
        self._load_history()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        添加消息到对话历史

        参数:
            role: 角色 (user/assistant/system)
            content: 消息内容
            metadata: 元数据 (可选)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        self.dialog_history.append(message)

        # 限制历史记录长度
        if len(self.dialog_history) > self.max_history:
            self.dialog_history.pop(0)

        # 保存历史记录
        self._save_history()

    def get_conversation(self) -> List[Dict[str, str]]:
        """
        获取当前对话历史

        返回:
            对话历史列表
        """
        return self.dialog_history

    def clear_history(self) -> None:
        """清空对话历史"""
        self.dialog_history = []
        self.context = {}
        self._save_history()

    def set_context(self, key: str, value: Any) -> None:
        """
        设置上下文变量

        参数:
            key: 变量名
            value: 变量值
        """
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        获取上下文变量

        参数:
            key: 变量名
            default: 默认值

        返回:
            变量值
        """
        return self.context.get(key, default)

    def _load_history(self) -> None:
        """从文件加载对话历史"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.dialog_history = data.get("history", [])
                    self.context = data.get("context", {})
            except Exception as e:
                logger.error(f"加载对话历史失败: {str(e)}")
                self.dialog_history = []
                self.context = {}

    def _save_history(self) -> None:
        """保存对话历史到文件"""
        try:
            data = {
                "history": self.dialog_history,
                "context": self.context
            }

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存对话历史失败: {str(e)}")
