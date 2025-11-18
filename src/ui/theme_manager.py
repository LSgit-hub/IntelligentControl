#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主题管理器模块
管理用户界面的主题和样式
"""

import os
import json
from typing import Dict, Any, List, Optional
from rich.theme import Theme
from rich.console import Console
from rich.style import Style

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ThemeManager:
    """主题管理器类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化主题管理器

        参数:
            config: 配置信息
        """
        self.config = config
        self.current_theme = config.get("current_theme", "default")
        self.themes_dir = config.get("themes_dir", os.path.expanduser("~/.intelligent_control/themes"))
        self.themes_file = config.get("themes_file", os.path.join(self.themes_dir, "themes.json"))

        # 确保主题目录存在
        os.makedirs(self.themes_dir, exist_ok=True)

        # 加载主题
        self.themes = {}
        self.load_themes()

        # 应用当前主题
        self.console = Console()
        self.apply_theme()

    def load_themes(self) -> None:
        """
        加载所有主题
        """
        try:
            # 加载内置主题
            self._load_builtin_themes()

            # 加载自定义主题
            if os.path.exists(self.themes_file):
                with open(self.themes_file, 'r', encoding='utf-8') as f:
                    custom_themes = json.load(f)
                    self.themes.update(custom_themes)

            logger.info(f"加载主题完成: {len(self.themes)} 个主题")

        except Exception as e:
            logger.error(f"加载主题失败: {str(e)}")
            # 使用默认主题
            self._load_builtin_themes()

    def _load_builtin_themes(self) -> None:
        """
        加载内置主题
        """
        # 默认主题
        self.themes["default"] = {
            "name": "默认",
            "description": "简洁的默认主题",
            "colors": {
                "primary": "cyan",
                "success": "green",
                "error": "red",
                "warning": "yellow",
                "info": "blue",
                "muted": "white",
                "highlight": "cyan"
            }
        }

        # 深色主题
        self.themes["dark"] = {
            "name": "深色",
            "description": "适合夜间使用的深色主题",
            "colors": {
                "primary": "bright_cyan",
                "success": "bright_green",
                "error": "bright_red",
                "warning": "bright_yellow",
                "info": "bright_blue",
                "muted": "white",
                "highlight": "bright_cyan",
                "background": "black",
                "surface": "dark_blue"
            }
        }

        # 高对比度主题
        self.themes["high_contrast"] = {
            "name": "高对比度",
            "description": "高对比度主题，适合视力不佳的用户",
            "colors": {
                "primary": "white",
                "success": "lime",
                "error": "bright_red",
                "warning": "bright_yellow",
                "info": "bright_cyan",
                "muted": "white",
                "highlight": "bold white",
                "background": "black",
                "surface": "black"
            }
        }

        # 彩虹主题
        self.themes["rainbow"] = {
            "name": "彩虹",
            "description": "多彩的彩虹主题",
            "colors": {
                "primary": "bold red",
                "success": "bold green",
                "error": "bold red",
                "warning": "bold yellow",
                "info": "bold blue",
                "muted": "white",
                "highlight": "magenta",
                "background": "black"
            }
        }

    def get_themes(self) -> Dict[str, Any]:
        """
        获取所有主题列表

        返回:
            主题列表
        """
        themes_info = []

        for theme_id, theme_data in self.themes.items():
            theme_info = {
                "id": theme_id,
                "name": theme_data["name"],
                "description": theme_data["description"],
                "current": theme_id == self.current_theme
            }
            themes_info.append(theme_info)

        return {
            "success": True,
            "themes": themes_info,
            "count": len(themes_info),
            "current": self.current_theme
        }

    def set_theme(self, theme_id: str) -> Dict[str, Any]:
        """
        设置当前主题

        参数:
            theme_id: 主题ID

        返回:
            操作结果
        """
        if theme_id not in self.themes:
            return {
                "success": False,
                "error": f"主题不存在: {theme_id}"
            }

        try:
            # 更新当前主题
            self.current_theme = theme_id

            # 应用主题
            self.apply_theme()

            # 保存配置
            self.save_config()

            logger.info(f"设置主题成功: {theme_id}")
            return {
                "success": True,
                "message": f"已设置主题: {self.themes[theme_id]['name']}",
                "theme_id": theme_id
            }

        except Exception as e:
            error_msg = f"设置主题失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def apply_theme(self) -> None:
        """
        应用当前主题
        """
        if self.current_theme not in self.themes:
            return

        theme_data = self.themes[self.current_theme]
        colors = theme_data.get("colors", {})

        # 创建Rich主题
        theme_styles = {}

        # 定义样式
        theme_styles["primary"] = Style(color=colors.get("primary", "cyan"))
        theme_styles["success"] = Style(color=colors.get("success", "green"))
        theme_styles["error"] = Style(color=colors.get("error", "red"))
        theme_styles["warning"] = Style(color=colors.get("warning", "yellow"))
        theme_styles["info"] = Style(color=colors.get("info", "blue"))
        theme_styles["muted"] = Style(color=colors.get("muted", "white"))
        theme_styles["highlight"] = Style(color=colors.get("highlight", "cyan"))

        # 应用主题到控制台
        try:
            theme = Theme(theme_styles)
            self.console.push_theme(theme)

            # 设置背景色
            if "background" in colors:
                self.console.style = Style(bgcolor=colors["background"])

            logger.info(f"应用主题成功: {self.current_theme}")

        except Exception as e:
            logger.error(f"应用主题失败: {str(e)}")

    def create_theme(self, theme_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新主题

        参数:
            theme_data: 主题数据

        返回:
            操作结果
        """
        try:
            theme_id = theme_data.get("id", "")
            theme_name = theme_data.get("name", "")
            theme_description = theme_data.get("description", "")
            colors = theme_data.get("colors", {})

            if not theme_id:
                return {
                    "success": False,
                    "error": "主题ID不能为空"
                }

            if not theme_name:
                return {
                    "success": False,
                    "error": "主题名称不能为空"
                }

            # 创建主题
            new_theme = {
                "name": theme_name,
                "description": theme_description,
                "colors": colors
            }

            # 添加到主题列表
            self.themes[theme_id] = new_theme

            # 保存主题
            self.save_themes()

            logger.info(f"创建主题成功: {theme_id}")
            return {
                "success": True,
                "message": f"已创建主题: {theme_name}",
                "theme_id": theme_id
            }

        except Exception as e:
            error_msg = f"创建主题失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def delete_theme(self, theme_id: str) -> Dict[str, Any]:
        """
        删除主题

        参数:
            theme_id: 主题ID

        返回:
            操作结果
        """
        if theme_id not in self.themes:
            return {
                "success": False,
                "error": f"主题不存在: {theme_id}"
            }

        # 不能删除默认主题
        if theme_id == "default":
            return {
                "success": False,
                "error": "不能删除默认主题"
            }

        try:
            # 删除主题
            del self.themes[theme_id]

            # 如果删除的是当前主题，切换到默认主题
            if self.current_theme == theme_id:
                self.current_theme = "default"
                self.apply_theme()

            # 保存主题
            self.save_themes()

            # 保存配置
            self.save_config()

            logger.info(f"删除主题成功: {theme_id}")
            return {
                "success": True,
                "message": f"已删除主题: {theme_id}",
                "theme_id": theme_id
            }

        except Exception as e:
            error_msg = f"删除主题失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def get_theme_colors(self, theme_id: str) -> Dict[str, Any]:
        """
        获取主题颜色配置

        参数:
            theme_id: 主题ID

        返回:
            主题颜色配置
        """
        if theme_id not in self.themes:
            return {
                "success": False,
                "error": f"主题不存在: {theme_id}"
            }

        theme_data = self.themes[theme_id]
        colors = theme_data.get("colors", {})

        return {
            "success": True,
            "theme_id": theme_id,
            "colors": colors
        }

    def update_theme_colors(self, theme_id: str, colors: Dict[str, str]) -> Dict[str, Any]:
        """
        更新主题颜色

        参数:
            theme_id: 主题ID
            colors: 新的颜色配置

        返回:
            操作结果
        """
        if theme_id not in self.themes:
            return {
                "success": False,
                "error": f"主题不存在: {theme_id}"
            }

        try:
            # 更新颜色
            self.themes[theme_id]["colors"].update(colors)

            # 如果是当前主题，重新应用
            if self.current_theme == theme_id:
                self.apply_theme()

            # 保存主题
            self.save_themes()

            logger.info(f"更新主题颜色成功: {theme_id}")
            return {
                "success": True,
                "message": f"已更新主题颜色: {theme_id}",
                "theme_id": theme_id
            }

        except Exception as e:
            error_msg = f"更新主题颜色失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def save_themes(self) -> None:
        """
        保存主题到文件
        """
        try:
            # 只保存自定义主题
            custom_themes = {}
            for theme_id, theme_data in self.themes.items():
                if theme_id not in ["default", "dark", "high_contrast", "rainbow"]:
                    custom_themes[theme_id] = theme_data

            if custom_themes:
                with open(self.themes_file, 'w', encoding='utf-8') as f:
                    json.dump(custom_themes, f, ensure_ascii=False, indent=2)

            logger.info("主题保存成功")

        except Exception as e:
            logger.error(f"保存主题失败: {str(e)}")

    def save_config(self) -> None:
        """
        保存配置
        """
        try:
            config_data = {
                "current_theme": self.current_theme
            }

            config_file = os.path.join(self.themes_dir, "config.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            logger.info("配置保存成功")

        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")

    def preview_theme(self, theme_id: str) -> Dict[str, Any]:
        """
        预览主题

        参数:
            theme_id: 主题ID

        返回:
            预览结果
        """
        if theme_id not in self.themes:
            return {
                "success": False,
                "error": f"主题不存在: {theme_id}"
            }

        theme_data = self.themes[theme_id]
        colors = theme_data.get("colors", {})

        # 创建预览文本
        preview_text = f"""
主题预览: {theme_data['name']}
{theme_data['description']}

颜色预览:
"""

        # 添加颜色预览
        for color_name, color_value in colors.items():
            preview_text += f"[{color_value}]{color_name}:[/] "

        return {
            "success": True,
            "theme_id": theme_id,
            "preview_text": preview_text
        }
