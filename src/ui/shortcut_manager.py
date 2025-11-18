#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
快捷键管理器模块
管理用户界面的快捷键绑定
"""

import os
import json
import keyboard
from typing import Dict, Any, List, Optional, Callable

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ShortcutManager:
    """快捷键管理器类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化快捷键管理器

        参数:
            config: 配置信息
        """
        self.config = config
        self.shortcuts_dir = config.get("shortcuts_dir", os.path.expanduser("~/.intelligent_control/shortcuts"))
        self.shortcuts_file = config.get("shortcuts_file", os.path.join(self.shortcuts_dir, "shortcuts.json"))

        # 确保快捷键目录存在
        os.makedirs(self.shortcuts_dir, exist_ok=True)

        # 快捷键绑定
        self.shortcuts = {}
        self.handlers = {}
        self.hotkeys = {}

        # 加载快捷键
        self.load_shortcuts()

        # 注册全局快捷键
        self.register_global_shortcuts()

    def load_shortcuts(self) -> None:
        """
        加载快捷键配置
        """
        try:
            # 加载默认快捷键
            self._load_default_shortcuts()

            # 加载自定义快捷键
            if os.path.exists(self.shortcuts_file):
                with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
                    custom_shortcuts = json.load(f)
                    self.shortcuts.update(custom_shortcuts)

            logger.info(f"加载快捷键完成: {len(self.shortcuts)} 个快捷键")

        except Exception as e:
            logger.error(f"加载快捷键失败: {str(e)}")
            # 使用默认快捷键
            self._load_default_shortcuts()

    def _load_default_shortcuts(self) -> None:
        """
        加载默认快捷键
        """
        # 默认快捷键
        self.shortcuts = {
            "help": {
                "key": "f1",
                "description": "显示帮助信息",
                "category": "通用"
            },
            "clear": {
                "key": "ctrl+l",
                "description": "清空屏幕",
                "category": "通用"
            },
            "exit": {
                "key": "ctrl+c",
                "description": "退出程序",
                "category": "通用"
            },
            "history": {
                "key": "f2",
                "description": "显示历史记录",
                "category": "通用"
            },
            "copy": {
                "key": "ctrl+c",
                "description": "复制选中的文本",
                "category": "编辑"
            },
            "paste": {
                "key": "ctrl+v",
                "description": "粘贴文本",
                "category": "编辑"
            },
            "cut": {
                "key": "ctrl+x",
                "description": "剪切选中的文本",
                "category": "编辑"
            },
            "save": {
                "key": "ctrl+s",
                "description": "保存当前会话",
                "category": "文件"
            },
            "open": {
                "key": "ctrl+o",
                "description": "打开文件",
                "category": "文件"
            },
            "new": {
                "key": "ctrl+n",
                "description": "新建会话",
                "category": "文件"
            },
            "theme": {
                "key": "f3",
                "description": "切换主题",
                "category": "界面"
            },
            "fullscreen": {
                "key": "f11",
                "description": "全屏模式",
                "category": "界面"
            },
            "zoom_in": {
                "key": "ctrl+plus",
                "description": "放大字体",
                "category": "界面"
            },
            "zoom_out": {
                "key": "ctrl+minus",
                "description": "缩小字体",
                "category": "界面"
            },
            "zoom_reset": {
                "key": "ctrl+0",
                "description": "重置字体大小",
                "category": "界面"
            }
        }

    def get_shortcuts(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        获取快捷键列表

        参数:
            category: 快捷键分类

        返回:
            快捷键列表
        """
        shortcuts_info = []

        for shortcut_id, shortcut_data in self.shortcuts.items():
            if category and shortcut_data.get("category") != category:
                continue

            shortcut_info = {
                "id": shortcut_id,
                "key": shortcut_data["key"],
                "description": shortcut_data["description"],
                "category": shortcut_data.get("category", "通用"),
                "handler": shortcut_id in self.handlers
            }
            shortcuts_info.append(shortcut_info)

        # 按分类排序
        if category:
            return {
                "success": True,
                "shortcuts": shortcuts_info,
                "count": len(shortcuts_info),
                "category": category
            }
        else:
            # 返回所有分类
            categories = {}
            for shortcut in shortcuts_info:
                cat = shortcut["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(shortcut)

            return {
                "success": True,
                "shortcuts": shortcuts_info,
                "categories": categories,
                "count": len(shortcuts_info)
            }

    def register_shortcut(self, shortcut_id: str, key: str, handler: Callable, description: str = "", category: str = "自定义") -> Dict[str, Any]:
        """
        注册快捷键

        参数:
            shortcut_id: 快捷键ID
            key: 快捷键
            handler: 处理函数
            description: 描述
            category: 分类

        返回:
            操作结果
        """
        try:
            # 注册快捷键
            keyboard.add_hotkey(key, handler)

            # 保存快捷键信息
            self.shortcuts[shortcut_id] = {
                "key": key,
                "description": description,
                "category": category
            }

            # 保存处理函数
            self.handlers[shortcut_id] = handler

            # 保存配置
            self.save_shortcuts()

            logger.info(f"注册快捷键成功: {shortcut_id} - {key}")
            return {
                "success": True,
                "message": f"已注册快捷键: {key}",
                "shortcut_id": shortcut_id,
                "key": key
            }

        except Exception as e:
            error_msg = f"注册快捷键失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def unregister_shortcut(self, shortcut_id: str) -> Dict[str, Any]:
        """
        注销快捷键

        参数:
            shortcut_id: 快捷键ID

        返回:
            操作结果
        """
        if shortcut_id not in self.shortcuts:
            return {
                "success": False,
                "error": f"快捷键不存在: {shortcut_id}"
            }

        try:
            # 移除快捷键
            key = self.shortcuts[shortcut_id]["key"]
            keyboard.remove_hotkey(key)

            # 删除快捷键信息
            del self.shortcuts[shortcut_id]

            # 删除处理函数
            if shortcut_id in self.handlers:
                del self.handlers[shortcut_id]

            # 保存配置
            self.save_shortcuts()

            logger.info(f"注销快捷键成功: {shortcut_id}")
            return {
                "success": True,
                "message": f"已注销快捷键: {shortcut_id}",
                "shortcut_id": shortcut_id
            }

        except Exception as e:
            error_msg = f"注销快捷键失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def update_shortcut(self, shortcut_id: str, key: str, description: str = "", category: str = "自定义") -> Dict[str, Any]:
        """
        更新快捷键

        参数:
            shortcut_id: 快捷键ID
            key: 新的快捷键
            description: 新的描述
            category: 新的分类

        返回:
            操作结果
        """
        if shortcut_id not in self.shortcuts:
            return {
                "success": False,
                "error": f"快捷键不存在: {shortcut_id}"
            }

        try:
            # 移除旧的快捷键
            old_key = self.shortcuts[shortcut_id]["key"]
            keyboard.remove_hotkey(old_key)

            # 添加新的快捷键
            if shortcut_id in self.handlers:
                keyboard.add_hotkey(key, self.handlers[shortcut_id])

            # 更新快捷键信息
            self.shortcuts[shortcut_id].update({
                "key": key,
                "description": description,
                "category": category
            })

            # 保存配置
            self.save_shortcuts()

            logger.info(f"更新快捷键成功: {shortcut_id} - {key}")
            return {
                "success": True,
                "message": f"已更新快捷键: {key}",
                "shortcut_id": shortcut_id,
                "key": key
            }

        except Exception as e:
            error_msg = f"更新快捷键失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def register_global_shortcuts(self) -> None:
        """
        注册全局快捷键
        """
        try:
            # 注册默认快捷键
            for shortcut_id, shortcut_data in self.shortcuts.items():
                if shortcut_id in self.handlers:
                    keyboard.add_hotkey(shortcut_data["key"], self.handlers[shortcut_id])
                    self.hotkeys[shortcut_id] = shortcut_data["key"]

            logger.info(f"注册全局快捷键完成: {len(self.hotkeys)} 个快捷键")

        except Exception as e:
            logger.error(f"注册全局快捷键失败: {str(e)}")

    def unregister_all_shortcuts(self) -> Dict[str, Any]:
        """
        注销所有快捷键

        返回:
            操作结果
        """
        try:
            # 注销所有快捷键
            for shortcut_id, key in self.hotkeys.items():
                keyboard.remove_hotkey(key)

            # 清空快捷键
            self.hotkeys = {}

            logger.info("注销所有快捷键成功")
            return {
                "success": True,
                "message": "已注销所有快捷键"
            }

        except Exception as e:
            error_msg = f"注销所有快捷键失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def save_shortcuts(self) -> None:
        """
        保存快捷键配置
        """
        try:
            # 只保存自定义快捷键
            custom_shortcuts = {}
            for shortcut_id, shortcut_data in self.shortcuts.items():
                if shortcut_id not in ["help", "clear", "exit", "history", "copy", "paste", "cut", "save", "open", "new", "theme", "fullscreen", "zoom_in", "zoom_out", "zoom_reset"]:
                    custom_shortcuts[shortcut_id] = shortcut_data

            if custom_shortcuts:
                with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_shortcuts, f, ensure_ascii=False, indent=2)

            logger.info("保存快捷键配置成功")

        except Exception as e:
            logger.error(f"保存快捷键配置失败: {str(e)}")

    def get_shortcut_key(self, shortcut_id: str) -> Optional[str]:
        """
        获取快捷键

        参数:
            shortcut_id: 快捷键ID

        返回:
            快捷键，如果不存在则返回None
        """
        return self.shortcuts.get(shortcut_id, {}).get("key")

    def execute_shortcut(self, shortcut_id: str) -> Dict[str, Any]:
        """
        执行快捷键

        参数:
            shortcut_id: 快捷键ID

        返回:
            执行结果
        """
        if shortcut_id not in self.handlers:
            return {
                "success": False,
                "error": f"快捷键不存在: {shortcut_id}"
            }

        try:
            # 执行处理函数
            handler = self.handlers[shortcut_id]
            handler()

            logger.info(f"执行快捷键成功: {shortcut_id}")
            return {
                "success": True,
                "message": f"已执行快捷键: {shortcut_id}",
                "shortcut_id": shortcut_id
            }

        except Exception as e:
            error_msg = f"执行快捷键失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def is_shortcut_registered(self, shortcut_id: str) -> bool:
        """
        检查快捷键是否已注册

        参数:
            shortcut_id: 快捷键ID

        返回:
            是否已注册
        """
        return shortcut_id in self.handlers

    def get_shortcut_statistics(self) -> Dict[str, Any]:
        """
        获取快捷键统计信息

        返回:
            统计信息
        """
        total_count = len(self.shortcuts)
        registered_count = len(self.handlers)

        # 统计分类
        categories = {}
        for shortcut_data in self.shortcuts.values():
            category = shortcut_data.get("category", "通用")
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        return {
            "success": True,
            "total_count": total_count,
            "registered_count": registered_count,
            "unregistered_count": total_count - registered_count,
            "categories": categories
        }
