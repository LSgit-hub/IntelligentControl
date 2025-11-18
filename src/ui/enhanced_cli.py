#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强的命令行界面模块
提供更好的用户体验和交互功能
"""

import os
import sys
import time
import threading
import signal
from typing import Dict, Any, List, Optional, Callable
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.theme import Theme

from .theme_manager import ThemeManager
from .shortcut_manager import ShortcutManager
from src.utils.logger import setup_logger

# 导入命令处理器 (延迟导入以避免循环导入)
# from core.command_handler import CommandHandler

logger = setup_logger(__name__)

class SimpleCommandHandler:
    """简单的命令处理器"""

    def __init__(self, cli_instance):
        self.cli = cli_instance

    def handle_command(self, command_str: str) -> bool:
        """处理命令"""
        try:
            # 基本命令处理
            if command_str.lower() == "help":
                self.cli.show_help()
                return True
            elif command_str.lower() == "clear":
                self.cli.clear_screen()
                return True
            elif command_str.lower() == "exit":
                self.cli.running = False
                return True
            elif command_str.lower().startswith("theme"):
                self.cli.handle_theme_command(command_str)
                return True
            elif command_str.lower().startswith("shortcut"):
                self.cli.handle_shortcut_command(command_str)
                return True
            elif command_str.lower() == "ui status":
                self.cli.show_ui_status()
                return True

            return False

        except Exception as e:
            logger.error(f"处理命令失败: {str(e)}")
            return False

class EnhancedCLI:
    """增强的命令行界面类"""

    def __init__(self, config: Dict[str, Any], command_handler: Optional[Any] = None):
        """
        初始化增强的命令行界面

        参数:
            config: 配置信息
            command_handler: 命令处理器
        """
        self.config = config
        self.console = Console()

        # 初始化命令处理器
        self.command_handler = SimpleCommandHandler(self)

        # 初始化主题管理器
        self.theme_manager = ThemeManager(config)

        # 移除快捷键管理器以避免全局冲突
        # self.shortcut_manager = ShortcutManager(config)

        # 界面状态
        self.running = True
        self.command_history = []
        self.max_history = config.get("max_history", 100)

        # 消息队列
        self.message_queue = []
        self.max_messages = 50

        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def run(self) -> None:
        """
        运行增强的命令行界面
        """
        try:
            # 显示欢迎信息
            self.show_welcome()

            # 主循环
            while self.running:
                # 处理消息队列
                self._process_messages()

                # 处理输入
                self._handle_input()

                # 短暂休眠
                time.sleep(0.01)

        except KeyboardInterrupt:
            self._signal_handler(signal.SIGINT, None)
        except Exception as e:
            logger.error(f"界面运行错误: {str(e)}")
        finally:
            self.cleanup()


    def show_welcome(self) -> None:
        """
        显示欢迎信息
        """
        welcome_text = """
# 智能控制系统

## 欢迎使用智能控制系统！

### 功能特性：
- 🔧 系统管理工具
- 📁 文件系统工具
- 🤖 AI接口集成
- 🎨 主题定制
- ⌨️ 快捷键支持

### 快捷键：
- F1: 帮助
- Ctrl+L: 清屏
- Ctrl+C: 退出
- F2: 历史记录
- F3: 切换主题
- F11: 全屏

### 开始使用：
输入 `help` 查看所有可用命令，或直接输入命令开始使用。
        """

        markdown = Markdown(welcome_text)
        self.console.print(Panel(markdown, title="欢迎使用", border_style="blue"))


    def _handle_input(self) -> None:
        """
        处理用户输入
        """
        try:
            # 使用标准输入处理
            command = input("[智能控制助手] >>> ").strip()
            if command:
                self.process_input(command)
        except KeyboardInterrupt:
            self.running = False
        except EOFError:
            self.running = False
        except Exception as e:
            logger.error(f"处理输入失败: {str(e)}")

    def process_input(self, command: str) -> None:
        """
        处理用户输入

        参数:
            command: 用户输入的命令
        """
        try:
            # 添加到历史记录
            self.add_to_history(command)

            # 处理命令
            if command.strip():
                # 添加到消息队列
                self.add_message(f"命令: {command}")

                # 调用命令处理器
                if not self.command_handler.handle_command(command):
                    self.add_message(f"未知命令: {command}")
                    self.add_message("输入 'help' 查看可用命令")

        except Exception as e:
            logger.error(f"处理命令失败: {str(e)}")
            self.add_message(f"错误: {str(e)}")

    def add_message(self, message: str) -> None:
        """
        添加消息到消息队列

        参数:
            message: 消息内容
        """
        try:
            # 添加时间戳
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"

            # 添加到队列
            self.message_queue.append(formatted_message)

            # 限制队列长度
            if len(self.message_queue) > self.max_messages:
                self.message_queue.pop(0)

        except Exception as e:
            logger.error(f"添加消息失败: {str(e)}")

    def add_to_history(self, command: str) -> None:
        """
        添加命令到历史记录

        参数:
            command: 命令内容
        """
        try:
            # 添加到历史记录
            self.command_history.append({
                "command": command,
                "timestamp": time.time()
            })

            # 限制历史记录长度
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)

        except Exception as e:
            logger.error(f"添加历史记录失败: {str(e)}")

    def show_help(self) -> None:
        """
        显示帮助信息
        """
        try:
            help_text = """
# 智能控制系统 - 帮助

## 基本命令：
- `help` - 显示帮助信息
- `clear` - 清空屏幕
- `exit` - 退出程序
- `history` - 显示命令历史

## 系统命令：
- `sysinfo` - 显示系统信息
- `ps` - 显示进程列表
- `kill <PID>` - 终止进程
- `services` - 显示服务列表

## 文件命令：
- `ls` - 列出文件
- `cd <目录>` - 切换目录
- `cat <文件>` - 显示文件内容
- `copy <源> <目标>` - 复制文件

## AI命令：
- `ai <消息>` - 与AI对话
- `ai-providers` - 显示AI服务提供商
- `ai-models` - 显示可用模型

## 主题命令：
- `themes` - 显示主题列表
- `theme <主题ID>` - 切换主题
- `theme create` - 创建新主题

## 快捷键命令：
- `shortcuts` - 显示快捷键列表
- `shortcut register <键> <描述>` - 注册快捷键
- `shortcut unregister <ID>` - 注销快捷键
            """

            markdown = Markdown(help_text)
            self.console.print(Panel(markdown, title="帮助", border_style="blue"))

        except Exception as e:
            logger.error(f"显示帮助失败: {str(e)}")

    def clear_screen(self) -> None:
        """
        清空屏幕
        """
        try:
            # 清空消息队列
            self.message_queue = []

            # 清空屏幕
            self.console.clear()

            # 重新显示欢迎信息
            self.show_welcome()

        except Exception as e:
            logger.error(f"清空屏幕失败: {str(e)}")

    def handle_theme_command(self, command: str) -> None:
        """
        处理主题命令

        参数:
            command: 主题命令
        """
        try:
            parts = command.split()

            if len(parts) == 1:
                # 显示主题列表
                result = self.theme_manager.get_themes()
                if result.get("success"):
                    themes = result.get("themes", [])
                    self.console.print("[bold blue]可用主题:[/bold blue]")
                    for theme in themes:
                        status = "[bold green](当前)[/bold green]" if theme.get("current") else ""
                        self.console.print(f"  {theme['id']}: {theme['name']} - {theme['description']} {status}")
            elif len(parts) == 2 and parts[1] == "create":
                # 创建新主题
                theme_name = Prompt.ask("请输入主题名称")
                theme_id = theme_name.lower().replace(" ", "_")

                theme_data = {
                    "id": theme_id,
                    "name": theme_name,
                    "description": Prompt.ask("请输入主题描述", default="自定义主题"),
                    "colors": {}
                }

                result = self.theme_manager.create_theme(theme_data)
                if result.get("success"):
                    self.console.print(f"[bold green]{result.get('message')}[/bold green]")
                else:
                    self.console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
            elif len(parts) == 2:
                # 切换主题
                theme_id = parts[1]
                result = self.theme_manager.set_theme(theme_id)
                if result.get("success"):
                    self.console.print(f"[bold green]{result.get('message')}[/bold green]")
                else:
                    self.console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
            else:
                self.console.print("[bold red]错误: 无效的主题命令[/bold red]")

        except Exception as e:
            logger.error(f"处理主题命令失败: {str(e)}")
            self.console.print(f"[bold red]错误: {str(e)}[/bold red]")

    def handle_shortcut_command(self, command: str) -> None:
        """
        处理快捷键命令 (已简化，移除全局快捷键功能)

        参数:
            command: 快捷键命令
        """
        self.console.print("[bold yellow]快捷键功能已禁用以避免冲突[/bold yellow]")
        self.console.print("如需快捷键功能，请在应用程序级别配置")

    def _signal_handler(self, signum, frame) -> None:
        """
        信号处理器

        参数:
            signum: 信号编号
            frame: 堆栈帧
        """
        if signum == signal.SIGINT:
            self.console.print("\n[yellow]正在退出...[/yellow]")
            self.running = False
        elif signum == signal.SIGTERM:
            self.console.print("\n[yellow]程序终止...[/yellow]")
            self.running = False

    def _process_messages(self) -> None:
        """
        处理消息队列
        """
        # 这里可以添加异步消息处理逻辑
        pass

    def cleanup(self) -> None:
        """
        清理资源
        """
        try:
            # 保存主题配置
            self.theme_manager.save_config()

            logger.info("界面清理完成")

        except Exception as e:
            logger.error(f"清理资源失败: {str(e)}")


    def show_ui_status(self) -> None:
        """
        显示UI状态
        """
        try:
            status_info = {
                "running": self.running,
                "theme": self.theme_manager.current_theme,
                "messages": len(self.message_queue),
                "history": len(self.command_history)
            }

            self.console.print("[bold blue]UI状态:[/bold blue]")
            for key, value in status_info.items():
                self.console.print(f"  {key}: {value}")

        except Exception as e:
            logger.error(f"显示UI状态失败: {str(e)}")
            self.console.print(f"[bold red]错误: {str(e)}[/bold red]")
