#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试用例模块
包含各种功能的具体测试用例
"""

import os
import sys
import tempfile
import shutil
from typing import Dict, Any, List, Optional

# 导入被测试的模块
from tools.system_tools import SystemTools
from tools.process_manager import ProcessManager
from tools.service_manager import ServiceManager
from tools.file_manager import FileManager
from tools.file_search import FileSearch
from tools.file_comparator import FileComparator
from ai_interface.ai_manager import AIManager
from ui.theme_manager import ThemeManager
from ui.shortcut_manager import ShortcutManager
from ui.enhanced_cli import EnhancedCLI
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TestCases:
    """测试用例类"""

    def __init__(self):
        """初始化测试用例"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileManager()
        self.process_manager = ProcessManager()
        self.service_manager = ServiceManager()
        self.file_search = FileSearch()
        self.file_comparator = FileComparator()

        logger.info(f"创建临时测试目录: {self.temp_dir}")

    def cleanup(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
            logger.info(f"清理临时测试目录: {self.temp_dir}")
        except Exception as e:
            logger.error(f"清理测试环境失败: {str(e)}")

    # ===== 系统功能测试 =====

    def test_system_info(self) -> bool:
        """测试系统信息获取"""
        try:
            system_tools = SystemTools()

            # 测试基本系统信息
            result = system_tools.get_system_info()
            assert result.get("success"), "系统信息获取失败"

            # 测试硬件信息
            result = system_tools.get_hardware_info()
            assert result.get("success"), "硬件信息获取失败"

            # 测试用户信息
            result = system_tools.get_users_info()
            assert result.get("success"), "用户信息获取失败"

            logger.info("系统信息测试通过")
            return True

        except Exception as e:
            logger.error(f"系统信息测试失败: {str(e)}")
            return False

    def test_process_management(self) -> bool:
        """测试进程管理"""
        try:
            # 获取当前进程列表
            processes = self.process_manager.list_processes()
            assert len(processes) > 0, "进程列表为空"

            # 获取当前进程信息
            current_pid = os.getpid()
            process_info = self.process_manager.get_process_info(current_pid)
            assert process_info is not None, "无法获取当前进程信息"

            # 测试进程搜索
            search_results = self.process_manager.search_processes("python")
            assert len(search_results) > 0, "进程搜索结果为空"

            logger.info("进程管理测试通过")
            return True

        except Exception as e:
            logger.error(f"进程管理测试失败: {str(e)}")
            return False

    def test_service_management(self) -> bool:
        """测试服务管理"""
        try:
            # 获取服务列表
            services = self.service_manager.list_services()
            assert len(services) > 0, "服务列表为空"

            # 获取特定服务信息
            service_info = self.service_manager.get_service_info("Winmgmt")
            assert service_info is not None, "无法获取服务信息"

            logger.info("服务管理测试通过")
            return True

        except Exception as e:
            logger.error(f"服务管理测试失败: {str(e)}")
            return False

    # ===== 文件系统测试 =====

    def test_file_operations(self) -> bool:
        """测试文件操作"""
        try:
            # 创建测试文件
            test_file = os.path.join(self.temp_dir, "test_file.txt")
            self.file_manager.create_file(test_file, "测试内容")

            # 检查文件是否存在
            assert os.path.exists(test_file), "文件创建失败"

            # 读取文件内容
            content = self.file_manager.read_file(test_file)
            assert content == "测试内容", "文件内容不匹配"

            # 复制文件
            copy_file = os.path.join(self.temp_dir, "copy_file.txt")
            self.file_manager.copy_file(test_file, copy_file)
            assert os.path.exists(copy_file), "文件复制失败"

            # 删除文件
            self.file_manager.delete_file(test_file)
            assert not os.path.exists(test_file), "文件删除失败"

            # 创建测试目录
            test_dir = os.path.join(self.temp_dir, "test_dir")
            self.file_manager.create_directory(test_dir)
            assert os.path.exists(test_dir), "目录创建失败"

            # 列出目录内容
            dir_contents = self.file_manager.list_directory(self.temp_dir)
            assert len(dir_contents) > 0, "目录内容为空"

            logger.info("文件操作测试通过")
            return True

        except Exception as e:
            logger.error(f"文件操作测试失败: {str(e)}")
            return False

    def test_file_search(self) -> bool:
        """测试文件搜索"""
        try:
            # 创建测试文件结构
            test_files = [
                os.path.join(self.temp_dir, "file1.txt"),
                os.path.join(self.temp_dir, "file2.py"),
                os.path.join(self.temp_dir, "subdir", "file3.txt"),
                os.path.join(self.temp_dir, "subdir", "file4.py")
            ]

            # 创建测试文件
            for file_path in test_files:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write("test content")

            # 测试文件名搜索
            results = self.file_search.search_files(self.temp_dir, "*.txt")
            assert len(results) >= 2, "文件名搜索结果不正确"

            # 测试内容搜索
            results = self.file_search.search_content(self.temp_dir, "test")
            assert len(results) >= 4, "内容搜索结果不正确"

            # 测试递归搜索
            results = self.file_search.search_files(self.temp_dir, "*.py", recursive=True)
            assert len(results) >= 2, "递归搜索结果不正确"

            logger.info("文件搜索测试通过")
            return True

        except Exception as e:
            logger.error(f"文件搜索测试失败: {str(e)}")
            return False

    def test_file_comparison(self) -> bool:
        """测试文件比较"""
        try:
            # 创建测试文件
            file1 = os.path.join(self.temp_dir, "file1.txt")
            file2 = os.path.join(self.temp_dir, "file2.txt")
            file3 = os.path.join(self.temp_dir, "file3.txt")

            with open(file1, 'w') as f:
                f.write("相同内容")
            with open(file2, 'w') as f:
                f.write("相同内容")
            with open(file3, 'w') as f:
                f.write("不同内容")

            # 测试文件比较
            result = self.file_comparator.compare_files(file1, file2)
            assert result.get("identical"), "相同文件比较失败"

            result = self.file_comparator.compare_files(file1, file3)
            assert not result.get("identical"), "不同文件比较失败"

            # 测试目录比较
            dir1 = os.path.join(self.temp_dir, "dir1")
            dir2 = os.path.join(self.temp_dir, "dir2")

            os.makedirs(dir1)
            os.makedirs(dir2)

            with open(os.path.join(dir1, "same.txt"), 'w') as f:
                f.write("相同内容")
            with open(os.path.join(dir2, "same.txt"), 'w') as f:
                f.write("相同内容")
            with open(os.path.join(dir1, "diff1.txt"), 'w') as f:
                f.write("内容1")
            with open(os.path.join(dir2, "diff2.txt"), 'w') as f:
                f.write("内容2")

            result = self.file_comparator.compare_directories(dir1, dir2)
            assert not result.get("identical"), "不同目录比较失败"

            logger.info("文件比较测试通过")
            return True

        except Exception as e:
            logger.error(f"文件比较测试失败: {str(e)}")
            return False

    # ===== AI接口测试 =====

    def test_ai_chat(self) -> bool:
        """测试AI对话"""
        try:
            # 创建AI管理器（使用空配置）
            ai_manager = AIManager({
                "providers": {
                    "openai": {
                        "model": "gpt-3.5-turbo",
                        "api_key": "test_key"
                    }
                },
                "default_provider": "openai"
            })

            # 测试AI对话（由于没有真实API，这里只测试结构）
            result = ai_manager.chat("测试消息")
            assert result.get("success") or "error" in result, "AI对话结构测试失败"

            logger.info("AI对话测试通过")
            return True

        except Exception as e:
            logger.error(f"AI对话测试失败: {str(e)}")
            return False

    def test_ai_models(self) -> bool:
        """测试AI模型列表"""
        try:
            # 创建AI管理器
            ai_manager = AIManager({
                "providers": {
                    "openai": {
                        "model": "gpt-3.5-turbo",
                        "api_key": "test_key"
                    }
                },
                "default_provider": "openai"
            })

            # 测试获取模型列表
            result = ai_manager.get_models()
            assert result.get("success"), "获取模型列表失败"

            models = result.get("models", [])
            assert len(models) > 0, "模型列表为空"

            logger.info("AI模型列表测试通过")
            return True

        except Exception as e:
            logger.error(f"AI模型列表测试失败: {str(e)}")
            return False

    def test_ai_history(self) -> bool:
        """测试AI历史记录"""
        try:
            # 创建AI管理器
            ai_manager = AIManager({
                "providers": {
                    "openai": {
                        "model": "gpt-3.5-turbo",
                        "api_key": "test_key"
                    }
                },
                "default_provider": "openai"
            })

            # 测试获取历史记录
            result = ai_manager.get_conversation_history()
            assert result.get("success"), "获取历史记录失败"

            # 测试清除历史记录
            result = ai_manager.clear_conversation_history()
            assert result.get("success"), "清除历史记录失败"

            logger.info("AI历史记录测试通过")
            return True

        except Exception as e:
            logger.error(f"AI历史记录测试失败: {str(e)}")
            return False

    # ===== 用户界面测试 =====

    def test_theme_management(self) -> bool:
        """测试主题管理"""
        try:
            # 创建主题管理器
            theme_manager = ThemeManager({
                "current_theme": "default",
                "themes_dir": self.temp_dir,
                "themes_file": os.path.join(self.temp_dir, "themes.json")
            })

            # 测试获取主题列表
            result = theme_manager.get_themes()
            assert result.get("success"), "获取主题列表失败"

            themes = result.get("themes", [])
            assert len(themes) > 0, "主题列表为空"

            # 测试设置主题
            result = theme_manager.set_theme("default")
            assert result.get("success"), "设置主题失败"

            logger.info("主题管理测试通过")
            return True

        except Exception as e:
            logger.error(f"主题管理测试失败: {str(e)}")
            return False

    def test_shortcut_management(self) -> bool:
        """测试快捷键管理"""
        try:
            # 创建快捷键管理器
            shortcut_manager = ShortcutManager({
                "shortcuts_dir": self.temp_dir,
                "shortcuts_file": os.path.join(self.temp_dir, "shortcuts.json")
            })

            # 测试获取快捷键列表
            result = shortcut_manager.get_shortcuts()
            assert result.get("success"), "获取快捷键列表失败"

            shortcuts = result.get("shortcuts", [])
            assert len(shortcuts) > 0, "快捷键列表为空"

            # 测试注册快捷键
            def test_handler():
                pass

            result = shortcut_manager.register_shortcut(
                "test_shortcut", 
                "ctrl+test", 
                test_handler, 
                "测试快捷键"
            )
            assert result.get("success"), "注册快捷键失败"

            logger.info("快捷键管理测试通过")
            return True

        except Exception as e:
            logger.error(f"快捷键管理测试失败: {str(e)}")
            return False

    def test_enhanced_cli(self) -> bool:
        """测试增强CLI"""
        try:
            # 创建配置
            config = {
                "max_history": 10,
                "themes_dir": self.temp_dir,
                "shortcuts_dir": self.temp_dir
            }

            # 创建增强CLI（不运行）
            enhanced_cli = EnhancedCLI(config)

            # 测试基本功能
            assert hasattr(enhanced_cli, 'console'), "CLI控制台不存在"
            assert hasattr(enhanced_cli, 'theme_manager'), "主题管理器不存在"
            assert hasattr(enhanced_cli, 'shortcut_manager'), "快捷键管理器不存在"

            logger.info("增强CLI测试通过")
            return True

        except Exception as e:
            logger.error(f"增强CLI测试失败: {str(e)}")
            return False
