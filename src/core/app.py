#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用程序核心模块
负责协调各个组件，管理应用程序生命周期
"""

import os
import sys
from typing import Dict, Any, Optional

from src.utils.logger import setup_logger
from src.config.settings import load_settings
from .command_handler import CommandHandler
from .dialog_manager import DialogManager

logger = setup_logger(__name__)

class IntelligentControlApp:
    """智能控制助手应用程序类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化应用程序

        参数:
            config_path: 配置文件路径
        """
        # 加载配置
        self.settings = load_settings(config_path)

        # 初始化组件
        self.command_handler = CommandHandler(self.settings)
        self.dialog_manager = DialogManager(self.settings)

        # 运行状态
        self.running = True

    def run(self) -> None:
        """运行应用程序主循环"""
        logger.info("智能控制助手启动")

        # 显示欢迎信息
        self._show_welcome()

        # 主循环
        while self.running:
            try:
                # 获取用户输入
                command = input("[智能控制助手] >>> ").strip()

                # 处理命令
                if command:
                    self.running = self.command_handler.handle_command(command)

            except KeyboardInterrupt:
                print("\n[黄色]收到中断信号，正在退出...[/黄色]")
                self.running = False
            except EOFError:
                print("\n[黄色]收到结束信号，正在退出...[/黄色]")
                self.running = False
            except Exception as e:
                logger.error(f"发生错误: {str(e)}")
                print(f"[红色]错误: {str(e)}[/红色]")

        logger.info("智能控制助手关闭")

    def _show_welcome(self) -> None:
        """显示欢迎信息"""
        print("=" * 50)
        print("智能控制助手 (Intelligent Control Assistant)")
        print("=" * 50)
        print("输入 'help' 查看可用命令")
        print("输入 'exit' 或 'quit' 退出程序")
        print("=" * 50)

        # 显示当前AI提供商
        current_provider = self.command_handler.ai_manager.current_provider
        if current_provider:
            print(f"当前AI提供商: {current_provider}")
        else:
            print("警告: 未设置AI提供商，请使用 'ai-set' 命令设置")

        print()

def main(config_path: Optional[str] = None) -> None:
    """应用程序入口点"""
    try:
        app = IntelligentControlApp(config_path)
        app.run()
    except Exception as e:
        logger.error(f"应用程序启动失败: {str(e)}")
        print(f"[红色]应用程序启动失败: {str(e)}[/红色]")
        sys.exit(1)

if __name__ == "__main__":
    main()
