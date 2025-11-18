#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
命令处理模块
负责解析和执行用户命令
"""

import sys
import os
import shlex
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from src.utils.logger import setup_logger
from src.tools.system_tools import SystemTools
from src.tools.interpreter_tools import InterpreterTools
from src.tools.file_manager import FileManager
from src.tools.file_search import FileSearch
from src.tools.file_comparator import FileComparator
from src.tools.command_executor import CommandExecutor
from src.tools.process_manager import ProcessManager
from src.tools.service_manager import ServiceManager
from src.tools.system_info import SystemInfo
from src.tools.registry import RegistryManager
from src.tools.performance_monitor import PerformanceMonitor
from src.ai_interface.ai_manager import AIManager
from src.ui.theme_manager import ThemeManager
from src.ui.shortcut_manager import ShortcutManager
from src.ui.enhanced_cli import EnhancedCLI
# from src.tests.test_runner import TestRunner

console = Console()
logger = setup_logger(__name__)

class CommandHandler:
    """命令处理器类"""

    def __init__(self, settings: Dict[str, Any]):
        """
        初始化命令处理器

        参数:
            settings: 配置字典
        """
        self.settings = settings
        self.system_tools = SystemTools()
        self.interpreter_tools = InterpreterTools()
        self.file_manager = FileManager()
        self.file_search = FileSearch()
        self.file_comparator = FileComparator()

        # 初始化系统命令执行工具
        command_timeout = settings.get("tools", {}).get("timeout", 30)
        allowed_commands = settings.get("tools", {}).get("allowed_commands", None)
        blocked_commands = settings.get("tools", {}).get("blocked_commands", ["rm -rf /", "del /f /s /q"])

        self.command_executor = CommandExecutor(
            timeout=command_timeout,
            allowed_commands=allowed_commands,
            blocked_commands=blocked_commands
        )
        self.process_manager = ProcessManager()
        self.service_manager = ServiceManager()
        self.system_info = SystemInfo()
        self.registry_manager = RegistryManager()
        self.performance_monitor = PerformanceMonitor()
        # 准备AI配置
        ai_config = {
            "default_provider": self.settings.get("ai", {}).get("provider", "openai"),
            "default_model": self.settings.get("ai", {}).get("model", "gpt-3.5-turbo"),
            "config_file": os.path.join(os.path.expanduser("~"), ".intelligent_control", "ai_config.json"),
            "history_file": os.path.join(os.path.expanduser("~"), ".intelligent_control", "ai_history.json"),
            "providers": {
                "openai": self.settings.get("ai", {}),
                "lmstudio": self.settings.get("ai", {}).get("lmstudio", {})
            }
        }
        self.ai_manager = AIManager(ai_config)

        # 初始化用户界面优化工具
        self.theme_manager = ThemeManager(settings)
        self.enhanced_cli = EnhancedCLI(settings)

        self.command_history = []
        self.max_history = settings.get("ui", {}).get("history_size", 100)

        # 注册命令
        self.commands = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "clear": self.cmd_clear,
            "ls": self.cmd_list_files,
            "dir": self.cmd_list_files,
            "cd": self.cmd_change_directory,
            "pwd": self.cmd_print_working_directory,
            "cat": self.cmd_read_file,
            "echo": self.cmd_echo,
            "exec": self.cmd_execute,
            "python": self.cmd_python,
            "node": self.cmd_node,
            "sysinfo": self.cmd_system_info,
            "ai": self.cmd_ai,
            "ai-providers": self.cmd_ai_providers,
            "ai-models": self.cmd_ai_models,
            "ai-set": self.cmd_ai_set,
            "ai-history": self.cmd_ai_history,
            "history": self.cmd_history,
            "mcp": self.cmd_mcp,
            "settings": self.cmd_settings,
            # 核心文件系统命令
            "copy": self.cmd_copy,
            "move": self.cmd_move,
            "search": self.cmd_search,
            "find": self.cmd_find,
            # 简化系统命令
            "ps": self.cmd_ps,
            "kill": self.cmd_kill,
            # 基础系统信息
            "sysinfo-hardware": self.cmd_sysinfo_hardware,
            # 用户界面命令
            "theme": self.cmd_theme,
            "ui": self.cmd_ui
        }

    def handle_command(self, command_str: str) -> bool:
        """
        处理用户命令

        参数:
            command_str: 命令字符串

        返回:
            是否应该继续运行程序
        """
        # 添加到历史记录
        self.command_history.append(command_str)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

        # 解析命令
        try:
            parts = shlex.split(command_str)
            if not parts:
                return True

            cmd_name = parts[0].lower()
            args = parts[1:]

            # 查找并执行命令
            if cmd_name in self.commands:
                return self.commands[cmd_name](args)
            else:
                console.print(f"[bold red]未知命令: {cmd_name}[/bold red]")
                console.print("输入 'help' 查看可用命令")
                return True

        except ValueError as e:
            console.print(f"[bold red]命令解析错误: {str(e)}[/bold red]")
            return True
        except Exception as e:
            logger.error(f"命令执行错误: {str(e)}")
            console.print(f"[bold red]命令执行错误: {str(e)}[/bold red]")
            return True

    def cmd_help(self, args: List[str]) -> bool:
        """显示帮助信息"""
        table = Table(title="可用命令")
        table.add_column("命令", style="cyan", no_wrap=True)
        table.add_column("描述", style="green")

        for cmd, func in self.commands.items():
            if cmd.startswith("_"):
                continue

            # 获取命令文档
            doc = func.__doc__ or "无描述"
            doc = doc.split("\n")[0].strip()  # 只取第一行

            table.add_row(cmd, doc)

        console.print(table)
        return True

    def cmd_exit(self, args: List[str]) -> bool:
        """退出程序"""
        console.print("[bold yellow]再见！[/bold yellow]")
        return False

    def cmd_clear(self, args: List[str]) -> bool:
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
        return True

    def cmd_list_files(self, args: List[str]) -> bool:
        """列出当前目录或指定目录的文件"""
        path = args[0] if args else "."
        result = self.system_tools.list_files(path)

        if result.get("success"):
            table = Table(title=f"目录内容: {path}")
            table.add_column("名称", style="cyan")
            table.add_column("类型", style="green")
            table.add_column("大小", style="blue")

            for file in result["files"]:
                name = file["name"]
                file_type = "目录" if file["is_dir"] else "文件"
                size = self._format_size(file["size"]) if not file["is_dir"] else "-"

                table.add_row(name, file_type, size)

            console.print(table)
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_change_directory(self, args: List[str]) -> bool:
        """切换目录"""
        if not args:
            console.print("[bold red]错误: 请指定目录路径[/bold red]")
            return True

        path = args[0]
        try:
            os.chdir(path)
            console.print(f"已切换到目录: {os.getcwd()}")
        except Exception as e:
            console.print(f"[bold red]错误: 无法切换到目录 {path}: {str(e)}[/bold red]")

        return True

    def cmd_print_working_directory(self, args: List[str]) -> bool:
        """显示当前工作目录"""
        console.print(os.getcwd())
        return True

    def cmd_read_file(self, args: List[str]) -> bool:
        """读取文件内容"""
        if not args:
            console.print("[bold red]错误: 请指定文件路径[/bold red]")
            return True

        path = args[0]
        result = self.system_tools.read_file(path)

        if result.get("success"):
            console.print(Panel(result["content"], title=f"文件内容: {path}"))
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_echo(self, args: List[str]) -> bool:
        """输出文本"""
        text = " ".join(args)
        console.print(text)
        return True

    def cmd_execute(self, args: List[str]) -> bool:
        """执行系统命令"""
        if not args:
            console.print("[bold red]错误: 请指定要执行的命令[/bold red]")
            return True

        command = " ".join(args)
        result = self.system_tools.execute_command(command)

        if result.get("success"):
            if result.get("stdout"):
                console.print(result["stdout"])
            if result.get("stderr"):
                console.print(f"[bold red]错误输出:[/bold red]")
                console.print(result["stderr"])
            console.print(f"[bold green]命令执行完成，返回码: {result.get('return_code')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_python(self, args: List[str]) -> bool:
        """执行Python代码"""
        if not args:
            console.print("[bold red]错误: 请输入Python代码[/bold red]")
            return True

        code = " ".join(args)
        result = self.interpreter_tools.execute_code("python", code)

        self._display_code_result(result)
        return True

    def cmd_node(self, args: List[str]) -> bool:
        """执行Node.js代码"""
        if not args:
            console.print("[bold red]错误: 请输入Node.js代码[/bold red]")
            return True

        code = " ".join(args)
        result = self.interpreter_tools.execute_code("node", code)

        self._display_code_result(result)
        return True

    def cmd_system_info(self, args: List[str]) -> bool:
        """显示系统信息"""
        result = self.system_tools.get_system_info()

        if result.get("success"):
            info = result["info"]
            panel = Panel(
                f"操作系统: {info['os']}\n"
                f"平台: {info['platform']}\n"
                f"用户: {info['user']}\n"
                f"计算机名: {info['computer']}\n"
                f"用户目录: {info['home']}",
                title="系统信息"
            )
            console.print(panel)
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_ai(self, args: List[str]) -> bool:
        """与AI对话"""
        if not args:
            console.print("[bold red]错误: 请输入要发送给AI的消息[/bold red]")
            return True

        message = " ".join(args)

        # 获取当前AI提供商和模型
        provider = self.ai_manager.current_provider
        if not provider:
            console.print("[bold red]错误: 请先设置AI提供商 (使用 'ai-set' 命令)[/bold red]")
            return True

        # 调用AI
        result = self.ai_manager.chat(message)

        if result.get("success"):
            console.print(Panel(result["response"], title="AI回复"))
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_ai_providers(self, args: List[str]) -> bool:
        """列出可用的AI提供商"""
        try:
            providers = self.ai_manager.get_providers()
            if providers and providers.get("success"):
                provider_list = providers.get("providers", {})
                current = providers.get("current", "")

                console.print("[bold blue]AI服务提供商列表:[/bold blue]")
                for name, info in provider_list.items():
                    status = "[bold green](当前)[/bold green]" if name == current else ""
                    console.print(f"  {name}: {info.get('description', '')} {status}")
            else:
                console.print("[bold red]无法获取AI提供商列表[/bold red]")
        except Exception as e:
            console.print(f"[bold red]获取AI提供商列表时出错: {str(e)}[/bold red]")

        return True

    def cmd_ai_models(self, args: List[str]) -> bool:
        """列出AI提供商的可用模型"""
        try:
            provider = args[0] if args else None
            result = self.ai_manager.get_models(provider)

            if result.get("success"):
                models = result.get("models", [])
                provider_name = result.get("provider", "")

                console.print(f"[bold blue]可用模型列表 ({provider_name}):[/bold blue]")
                for model in models:
                    console.print(f"  {model}")
                console.print(f"[bold green]总计: {len(models)} 个模型[/bold green]")
            else:
                console.print(f"[bold red]无法获取模型列表: {result.get('error', '未知错误')}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]获取AI模型列表时出错: {str(e)}[/bold red]")

        return True

    def cmd_ai_set(self, args: List[str]) -> bool:
        """设置AI提供商和模型"""
        try:
            if not args:
                console.print("[bold red]错误: 请指定操作类型[/bold red]")
                console.print("用法: ai-set <provider|model> <名称>")
                return True

            action = args[0]
            name = args[1] if len(args) > 1 else None

            if action == "provider" and name:
                result = self.ai_manager.set_provider(name)
            elif action == "model" and name:
                result = self.ai_manager.set_model(name)
            else:
                console.print("[bold red]错误: 无效的操作类型或缺少参数[/bold red]")
                console.print("用法: ai-set <provider|model> <名称>")
                return True

            if result.get("success"):
                console.print(f"[bold green]{result.get('message')}[/bold green]")
            else:
                console.print(f"[bold red]设置失败: {result.get('error', '未知错误')}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]设置AI配置时出错: {str(e)}[/bold red]")

        return True

    def cmd_history(self, args: List[str]) -> bool:
        """显示命令历史"""
        if not self.command_history:
            console.print("[bold yellow]命令历史为空[/bold yellow]")
            return True

        table = Table(title="命令历史")
        table.add_column("#", style="cyan")
        table.add_column("命令", style="green")

        for i, cmd in enumerate(self.command_history[-20:], len(self.command_history) - 19):
            table.add_row(str(i), cmd)

        console.print(table)
        return True

    # 文件系统工具命令
    def cmd_copy(self, args: List[str]) -> bool:
        """复制文件或目录"""
        if len(args) < 2:
            console.print("[bold red]错误: 请指定源路径和目标路径[/bold red]")
            console.print("用法: copy <源路径> <目标路径> [overwrite]")
            return True

        src = args[0]
        dst = args[1]
        overwrite = args[2].lower() == "true" if len(args) > 2 else False

        result = self.file_manager.copy_file(src, dst, overwrite)

        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_move(self, args: List[str]) -> bool:
        """移动文件或目录"""
        if len(args) < 2:
            console.print("[bold red]错误: 请指定源路径和目标路径[/bold red]")
            console.print("用法: move <源路径> <目标路径> [overwrite]")
            return True

        src = args[0]
        dst = args[1]
        overwrite = args[2].lower() == "true" if len(args) > 2 else False

        result = self.file_manager.move_file(src, dst, overwrite)

        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_rename(self, args: List[str]) -> bool:
        """重命名文件或目录"""
        if len(args) < 2:
            console.print("[bold red]错误: 请指定路径和新名称[/bold red]")
            console.print("用法: rename <路径> <新名称> [overwrite]")
            return True

        path = args[0]
        new_name = args[1]
        overwrite = args[2].lower() == "true" if len(args) > 2 else False

        result = self.file_manager.rename_file(path, new_name, overwrite)

        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_search(self, args: List[str]) -> bool:
        """搜索文件"""
        if not args:
            console.print("[bold red]错误: 请指定搜索模式[/bold red]")
            console.print("用法: search <模式> [路径] [recursive] [case_sensitive]")
            return True

        pattern = args[0]
        path = args[1] if len(args) > 1 else "."
        recursive = args[2].lower() == "true" if len(args) > 2 else True
        case_sensitive = args[3].lower() == "true" if len(args) > 3 else False

        result = self.file_search.find_files(pattern, path, recursive, case_sensitive)

        if result.get("success"):
            matches = result.get("matches", [])
            if matches:
                table = Table(title=f"搜索结果: {pattern}")
                table.add_column("路径", style="cyan")

                for match in matches:
                    table.add_row(match)

                console.print(table)
                console.print(f"[bold green]找到 {len(matches)} 个匹配项[/bold green]")
            else:
                console.print(f"[bold yellow]未找到匹配项[/bold yellow]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_find(self, args: List[str]) -> bool:
        """查找文件（高级搜索）"""
        if not args:
            console.print("[bold red]错误: 请指定搜索类型和参数[/bold red]")
            console.print("用法: find <type> <pattern> [path] [options...]")
            console.print("类型: name, content, size, ext")
            return True

        search_type = args[0].lower()
        pattern = args[1] if len(args) > 1 else ""
        path = args[2] if len(args) > 2 else "."

        if search_type == "name":
            # 按名称查找
            recursive = args[3].lower() == "true" if len(args) > 3 else True
            case_sensitive = args[4].lower() == "true" if len(args) > 4 else False

            result = self.file_search.find_files(pattern, path, recursive, case_sensitive)
        elif search_type == "content":
            # 按内容查找
            recursive = args[3].lower() == "true" if len(args) > 3 else True
            case_sensitive = args[4].lower() == "true" if len(args) > 4 else False
            encoding = args[5] if len(args) > 5 else "utf-8"

            result = self.file_search.find_files_by_content(pattern, path, recursive, case_sensitive, encoding=encoding)
        elif search_type == "size":
            # 按大小查找
            try:
                min_size = int(args[3]) if len(args) > 3 and args[3] else None
                max_size = int(args[4]) if len(args) > 4 and args[4] else None
            except ValueError:
                console.print("[bold red]错误: 大小参数必须是整数[/bold red]")
                return True

            recursive = args[5].lower() == "true" if len(args) > 5 else True

            result = self.file_search.find_files_by_size(min_size, max_size, path, recursive)
        elif search_type == "ext":
            # 按扩展名查找
            recursive = args[3].lower() == "true" if len(args) > 3 else True

            result = self.file_search.find_files_by_extension(pattern, path, recursive)
        else:
            console.print(f"[bold red]错误: 不支持的搜索类型: {search_type}[/bold red]")
            return True

        if result.get("success"):
            matches = result.get("matches", [])
            if matches:
                table = Table(title=f"查找结果: {search_type} - {pattern}")
                table.add_column("路径", style="cyan")

                for match in matches:
                    table.add_row(match)

                console.print(table)
                console.print(f"[bold green]找到 {len(matches)} 个匹配项[/bold green]")
            else:
                console.print(f"[bold yellow]未找到匹配项[/bold yellow]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_compress(self, args: List[str]) -> bool:
        """压缩文件或目录"""
        if len(args) < 2:
            console.print("[bold red]错误: 请指定源路径和目标路径[/bold red]")
            console.print("用法: compress <源路径> <目标路径> [format]")
            return True

        src = args[0]
        dst = args[1]
        format = args[2] if len(args) > 2 else "zip"

        result = self.file_manager.compress_file(src, dst, format)

        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True

    def cmd_extract(self, args: List[str]) -> bool:
        """解压文件"""
        try:
            if not args:
                console.print("[bold red]错误: 请指定源路径[/bold red]")
                console.print("用法: extract <源路径> [目标路径]")
                return True

            src = args[0]
            dst = args[1] if len(args) > 1 else None

            result = self.file_manager.extract_file(src, dst or ".")

            if result.get("success"):
                console.print(f"[bold green]{result.get('message')}[/bold green]")
            else:
                console.print(f"[bold red]解压失败: {result.get('error', '未知错误')}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]解压文件时出错: {str(e)}[/bold red]")

        return True

    def cmd_compare(self, args: List[str]) -> bool:
        """比较文件或目录"""
        if len(args) < 2:
            console.print("[bold red]错误: 请指定两个路径[/bold red]")
            console.print("用法: compare <路径1> <路径2> [show_diff] [type]")
            console.print("类型: file, dir")
            return True

        path1 = args[0]
        path2 = args[1]
        show_diff = args[2].lower() == "true" if len(args) > 2 else False
        type = args[3].lower() if len(args) > 3 else "file"

        if type == "file":
            # 比较文件
            result = self.file_comparator.compare_files(path1, path2, show_diff)
        elif type == "dir":
            # 比较目录
            result = self.file_comparator.compare_directories(path1, path2, show_diff)
        else:
            console.print(f"[bold red]错误: 不支持的比较类型: {type}[/bold red]")
            return True

        try:
            if result.get("success"):
                if type == "file":
                    if result.get("equal"):
                        console.print("[bold green]文件相同[/bold green]")
                    else:
                        console.print("[bold yellow]文件不同[/bold yellow]")
                        diff_lines = result.get("diff")
                        if diff_lines and isinstance(diff_lines, list):
                            console.print(Panel("\n".join(diff_lines), title="差异"))
                else:
                    # 显示目录比较结果
                    console.print(f"[bold green]目录比较结果:[/bold green]")
                    console.print(f"  左独有: {len(result.get('left_only', []))} 个")
                    console.print(f"  右独有: {len(result.get('right_only', []))} 个")
                    console.print(f"  共有: {len(result.get('common', []))} 个")
                    console.print(f"  相同文件: {len(result.get('same_files', []))} 个")
                    console.print(f"  不同文件: {len(result.get('diff_files', []))} 个")
            else:
                console.print(f"[bold red]比较失败: {result.get('error', '未知错误')}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]比较文件时出错: {str(e)}[/bold red]")

        return True

    def cmd_duplicates(self, args: List[str]) -> bool:
        """查找重复文件"""
        if not args:
            console.print("[bold red]错误: 请指定搜索路径[/bold red]")
            console.print("用法: duplicates <路径> [recursive] [compare_content]")
            return True

        path = args[0]
        recursive = args[1].lower() == "true" if len(args) > 1 else True
        compare_content = args[2].lower() == "true" if len(args) > 2 else True

        result = self.file_comparator.find_duplicate_files(path, recursive, compare_content)

        if result.get("success"):
            groups = result.get("duplicate_groups", [])
            if groups:
                console.print(f"[bold green]找到 {len(groups)} 组重复文件:[/bold green]")

                for group in groups:
                    console.print(f"  大小: {group.get('size_str')} - {group.get('count')} 个文件")
                    for file in group.get("files", []):
                        console.print(f"    {file}")
            else:
                console.print("[bold yellow]未找到重复文件[/bold yellow]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

        return True
    
    # 系统命令执行工具命令
    def cmd_exec(self, args: List[str]) -> bool:
        """执行系统命令"""
        if not args:
            console.print("[bold red]错误: 请指定要执行的命令[/bold red]")
            console.print("用法: exec <命令> [timeout] [background] [cwd] [env]")
            return True
            
        command = args[0]
        timeout = int(args[1]) if len(args) > 1 and args[1] else None
        background = args[2].lower() == "true" if len(args) > 2 and args[2] else False
        cwd = args[3] if len(args) > 3 and args[3] else None
        env = None  # 暂时不支持环境变量传递
        
        result = self.command_executor.execute_command(
            command, timeout, background, cwd, env
        )
        
        if result.get("success"):
            if result.get("background"):
                console.print(f"[bold green]后台任务已启动: {result.get('task_id')}[/bold green]")
            else:
                if result.get("stdout"):
                    console.print(result.get("stdout"))
                if result.get("stderr"):
                    console.print(f"[bold red]错误输出:[/bold red]")
                    console.print(result.get("stderr"))
                console.print(f"[bold green]命令执行完成，返回码: {result.get('return_code')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_bg_tasks(self, args: List[str]) -> bool:
        """查看后台任务"""
        tasks = self.command_executor.get_background_tasks()
        
        if not tasks:
            console.print("[bold yellow]没有正在运行的后台任务[/bold yellow]")
            return True
        
        table = Table(title="后台任务")
        table.add_column("任务ID", style="cyan")
        table.add_column("命令", style="green")
        table.add_column("开始时间", style="blue")
        table.add_column("状态", style="yellow")
        
        for task_id, task in tasks.items():
            status = "运行中" if task.get("running") else "已完成"
            start_time = task.get("start_time", 0)
            from datetime import datetime
            time_str = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
            
            table.add_row(task_id, task.get("command", ""), time_str, status)
        
        console.print(table)
        return True
    
    def cmd_bg_stop(self, args: List[str]) -> bool:
        """停止后台任务"""
        if not args:
            console.print("[bold red]错误: 请指定任务ID[/bold red]")
            console.print("用法: bg-stop <任务ID>")
            return True
            
        task_id = args[0]
        result = self.command_executor.stop_background_task(task_id)
        
        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_bg_clear(self, args: List[str]) -> bool:
        """清除已完成的后台任务"""
        result = self.command_executor.clear_background_tasks()
        
        if result.get("success"):
            console.print(f"[bold green]已清除 {result.get('count')} 个已完成的后台任务[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ps(self, args: List[str]) -> bool:
        """列出进程"""
        detailed = args[0].lower() == "true" if args else False
        filter_name = args[1] if len(args) > 1 else None
        
        result = self.process_manager.list_processes(detailed, filter_name)
        
        if result.get("success"):
            processes = result.get("processes", [])
            if processes:
                table = Table(title=f"进程列表 (过滤: {filter_name or '无'})")
                table.add_column("PID", style="cyan")
                table.add_column("名称", style="green")
                table.add_column("CPU%", style="blue")
                table.add_column("内存%", style="magenta")
                table.add_column("状态", style="yellow")
                table.add_column("用户", style="red")
                
                for proc in processes:
                    pid = str(proc.get("pid", ""))
                    name = proc.get("name", "")
                    cpu = f"{proc.get('cpu_percent', 0):.1f}%"
                    mem = f"{proc.get('memory_percent', 0):.1f}%"
                    status = proc.get("status", "")
                    user = proc.get("username", "")
                    
                    table.add_row(pid, name, cpu, mem, status, user)
                
                console.print(table)
                console.print(f"[bold green]找到 {len(processes)} 个进程[/bold green]")
            else:
                console.print("[bold yellow]未找到进程[/bold yellow]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ps_info(self, args: List[str]) -> bool:
        """获取进程详细信息"""
        if not args:
            console.print("[bold red]错误: 请指定进程ID[/bold red]")
            console.print("用法: ps-info <PID>")
            return True
            
        pid = int(args[0])
        result = self.process_manager.get_process_info(pid)
        
        if result.get("success"):
            proc = result.get("process", {})
            info_text = f"PID: {proc.get('pid', '')}\n"
            info_text += f"名称: {proc.get('name', '')}\n"
            info_text += f"状态: {proc.get('status', '')}\n"
            info_text += f"CPU使用率: {proc.get('cpu_percent', 0):.1f}%\n"
            info_text += f"内存使用率: {proc.get('memory_percent', 0):.1f}%\n"
            info_text += f"命令行: {' '.join(proc.get('cmdline', []))}\n"
            info_text += f"工作目录: {proc.get('cwd', '')}\n"
            info_text += f"线程数: {proc.get('num_threads', 0)}\n"
            info_text += f"创建时间: {proc.get('create_time', '')}"
            
            console.print(Panel(info_text, title=f"进程信息 (PID: {pid})"))
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_kill(self, args: List[str]) -> bool:
        """终止进程"""
        if not args:
            console.print("[bold red]错误: 请指定进程ID[/bold red]")
            console.print("用法: kill <PID> [force]")
            return True
            
        pid = int(args[0])
        force = args[1].lower() == "true" if len(args) > 1 else False
        
        result = self.process_manager.kill_process(pid, force)
        
        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_services(self, args: List[str]) -> bool:
        """列出系统服务"""
        detailed = args[0].lower() == "true" if args else False
        
        result = self.service_manager.list_services(detailed)
        
        if result.get("success"):
            services = result.get("services", [])
            if services:
                table = Table(title=f"系统服务列表 ({result.get('system', '').upper()})")
                table.add_column("名称", style="cyan")
                table.add_column("状态", style="green")
                table.add_column("类型", style="blue")
                table.add_column("PID", style="magenta")
                
                for service in services:
                    name = service.get("name", "")
                    state = service.get("state", "")
                    type_ = service.get("type", "")
                    pid = service.get("process_id", "")
                    
                    table.add_row(name, state, type_, pid)
                
                console.print(table)
                console.print(f"[bold green]找到 {len(services)} 个服务[/bold green]")
            else:
                console.print("[bold yellow]未找到服务[/bold yellow]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_service_info(self, args: List[str]) -> bool:
        """获取服务详细信息"""
        if not args:
            console.print("[bold red]错误: 请指定服务名称[/bold red]")
            console.print("用法: service-info <服务名称>")
            return True
            
        name = args[0]
        result = self.service_manager.get_service_info(name)
        
        if result.get("success"):
            service = result.get("service", {})
            info_text = f"名称: {service.get('name', '')}\n"
            info_text += f"状态: {service.get('state', '')}\n"
            info_text += f"类型: {service.get('type', '')}\n"
            info_text += f"PID: {service.get('process_id', '')}"
            
            console.print(Panel(info_text, title=f"服务信息 ({name})"))
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    # 系统信息获取工具命令
    def cmd_sysinfo(self, args: List[str]) -> bool:
        """获取系统信息"""
        detailed = args[0].lower() == "true" if args else False
        
        result = self.system_info.get_basic_info()
        if result.get("success"):
            info = result.get("info", {})
            
            console.print(Panel(
                f"系统: {info.get('system', {}).get('name', '')}\n"
                f"版本: {info.get('system', {}).get('version', '')}\n"
                f"主机名: {info.get('network', {}).get('hostname', '')}\n"
                f"IP地址: {info.get('network', {}).get('ip_address', '')}\n"
                f"Python版本: {info.get('system', {}).get('python_version', '')}",
                title="系统信息"
            ))
            
            if detailed:
                console.print("\n[bold blue]详细信息:[/bold blue]")
                for key, value in info.items():
                    if key != "system":
                        console.print(f"  {key}: {value}")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_sysinfo_hardware(self, args: List[str]) -> bool:
        """获取硬件信息"""
        result = self.system_info.get_hardware_info()
        
        if result.get("success"):
            info = result.get("info", {})
            
            console.print(Panel(
                f"CPU核心数: {info.get('cpu', {}).get('count', 0)}\n"
                f"CPU使用率: {info.get('cpu', {}).get('usage_percent', 0):.1f}%\n"
                f"内存总量: {self._format_size(info.get('memory', {}).get('total', 0))}\n"
                f"内存使用率: {info.get('memory', {}).get('percent', 0):.1f}%\n"
                f"磁盘分区数: {len(info.get('disk', {}).get('partitions', []))}\n"
                f"网络接口数: {len(info.get('network', {}).get('interfaces', {}))}",
                title="硬件信息"
            ))
            
            # 显示磁盘分区信息
            if info.get('disk', {}).get('partitions'):
                console.print("\n[bold blue]磁盘分区:[/bold blue]")
                for partition in info['disk']['partitions']:
                    console.print(f"  {partition['device']}: {partition['mountpoint']} ({self._format_size(partition['total'])})")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_sysinfo_users(self, args: List[str]) -> bool:
        """获取用户信息"""
        result = self.system_info.get_users_info()
        
        if result.get("success"):
            info = result.get("info", {})
            
            console.print(Panel(
                f"当前用户: {info.get('current_user', {}).get('name', '')}\n"
                f"用户总数: {len(info.get('users', []))}\n"
                f"登录用户数: {len(info.get('logged_in_users', []))}",
                title="用户信息"
            ))
            
            # 显示登录用户
            if info.get('logged_in_users'):
                console.print("\n[bold blue]登录用户:[/bold blue]")
                for user in info['logged_in_users']:
                    console.print(f"  {user['name']} (终端: {user['terminal']}, 主机: {user['host']})")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_sysinfo_env(self, args: List[str]) -> bool:
        """获取环境变量"""
        result = self.system_info.get_environment_variables()
        
        if result.get("success"):
            info = result.get("info", {})
            variables = info.get('variables', {})
            
            console.print(f"环境变量总数: {info.get('count', 0)}")
            
            # 显示前20个环境变量
            console.print("\n[bold blue]环境变量:[/bold blue]")
            for i, (name, value) in enumerate(variables.items()):
                if i < 20:
                    console.print(f"  {name}={value}")
                else:
                    break
            
            if len(variables) > 20:
                console.print(f"  ... 还有 {len(variables) - 20} 个变量")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_sysinfo_network(self, args: List[str]) -> bool:
        """获取网络信息"""
        result = self.system_info.get_network_info()
        
        if result.get("success"):
            info = result.get("info", {})
            
            console.print(Panel(
                f"主机名: {info.get('interfaces', {}).get('hostname', '')}\n"
                f"网络连接数: {len(info.get('connections', []))}\n"
                f"网络接口数: {len(info.get('interfaces', {}))}",
                title="网络信息"
            ))
            
            # 显示网络接口
            if info.get('interfaces'):
                console.print("\n[bold blue]网络接口:[/bold blue]")
                for interface, addresses in info['interfaces'].items():
                    console.print(f"  {interface}:")
                    for addr in addresses:
                        console.print(f"    {addr['address']} ({addr['family']})")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_registry_hives(self, args: List[str]) -> bool:
        """列出注册表根项"""
        result = self.registry_manager.list_hives()
        
        if result.get("success"):
            hives = result.get('hives', [])
            
            table = Table(title="注册表根项")
            table.add_column("名称", style="cyan")
            table.add_column("描述", style="green")
            
            for hive in hives:
                table.add_row(hive["name"], hive["description"])
            
            console.print(table)
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_registry_keys(self, args: List[str]) -> bool:
        """列出注册表子项"""
        if not args:
            console.print("[bold red]错误: 请指定注册表路径[/bold red]")
            console.print("用法: registry-keys <路径>")
            return True
            
        path = args[0]
        result = self.registry_manager.list_keys(path)
        
        if result.get("success"):
            sub_keys = result.get('sub_keys', [])
            
            table = Table(title=f"注册表子项 ({path})")
            table.add_column("名称", style="cyan")
            table.add_column("路径", style="green")
            
            for key in sub_keys:
                table.add_row(key["name"], key["path"])
            
            console.print(table)
            console.print(f"[bold green]找到 {len(sub_keys)} 个子项[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_registry_values(self, args: List[str]) -> bool:
        """列出注册表值"""
        if not args:
            console.print("[bold red]错误: 请指定注册表路径[/bold red]")
            console.print("用法: registry-values <路径>")
            return True
            
        path = args[0]
        result = self.registry_manager.list_values(path)
        
        if result.get("success"):
            values = result.get('values', [])
            
            table = Table(title=f"注册表值 ({path})")
            table.add_column("名称", style="cyan")
            table.add_column("类型", style="green")
            table.add_column("数据", style="yellow")
            
            for value in values:
                table.add_row(value["name"], value["type"], str(value["data"]))
            
            console.print(table)
            console.print(f"[bold green]找到 {len(values)} 个值[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_perf_start(self, args: List[str]) -> bool:
        """开始性能监控"""
        interval = float(args[0]) if args and args[0] else 1.0
        
        result = self.performance_monitor.start_monitoring(interval)
        
        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_perf_stop(self, args: List[str]) -> bool:
        """停止性能监控"""
        result = self.performance_monitor.stop_monitoring()
        
        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_perf_stats(self, args: List[str]) -> bool:
        """获取当前性能统计信息"""
        try:
            result = self.performance_monitor.get_current_stats()

            if result.get("success"):
                stats = result.get('stats', {})

                console.print(Panel(
                    f"CPU使用率: {stats.get('cpu', {}).get('percent', 0):.1f}%\n"
                    f"内存使用率: {stats.get('memory', {}).get('percent', 0):.1f}%\n"
                    f"交换分区使用率: {stats.get('swap', {}).get('percent', 0):.1f}%\n"
                    f"活跃进程数: {stats.get('process_count', 0)}",
                    title="性能统计"
                ))
            else:
                console.print(f"[bold red]获取性能统计失败: {result.get('error', '未知错误')}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]获取性能统计时出错: {str(e)}[/bold red]")

        return True
    
    def cmd_perf_top(self, args: List[str]) -> bool:
        """获取资源使用率最高的进程"""
        limit = int(args[0]) if args and args[0] else 10
        by = args[1] if len(args) > 1 else "cpu"
        
        result = self.performance_monitor.get_top_processes(limit, by)
        
        if result.get("success"):
            processes = result.get('processes', [])
            
            table = Table(title=f"资源使用率最高的 {limit} 个进程 (按{by}排序)")
            table.add_column("PID", style="cyan")
            table.add_column("名称", style="green")
            table.add_column("CPU%", style="blue")
            table.add_column("内存%", style="magenta")
            
            for proc in processes:
                table.add_row(
                    str(proc.get("pid", "")),
                    proc.get("name", ""),
                    f"{proc.get('cpu_percent', 0):.1f}%",
                    f"{proc.get('memory_percent', 0):.1f}%"
                )
            
            console.print(table)
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    # AI接口集成命令
    def cmd_ai(self, args: List[str]) -> bool:
        """与AI对话"""
        if not args:
            console.print("[bold red]错误: 请输入消息[/bold red]")
            console.print("用法: ai <消息> [provider] [model]")
            return True
            
        message = args[0]
        provider = args[1] if len(args) > 1 else None
        model = args[2] if len(args) > 2 else None
        
        # 检查是否使用流式输出
        stream = False
        if "--stream" in args:
            stream = True
            args.remove("--stream")
        
        # 发送对话请求
        if stream:
            result = self.ai_manager.stream_chat(message, provider, model)
        else:
            result = self.ai_manager.chat(message, provider, model)
        
        if result.get("success"):
            console.print(f"[bold green]AI响应 ({result.get('provider', '')} - {result.get('model', '')}):[/bold green]")
            console.print(result.get("response", ""))
            
            # 显示统计信息
            if result.get("tokens_used"):
                console.print(f"[bold blue]Token使用: {result.get('tokens_used')}[/bold blue]")
            if result.get("time_used"):
                console.print(f"[bold blue]响应时间: {result.get('time_used'):.2f}秒[/bold blue]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ai_providers(self, args: List[str]) -> bool:
        """获取AI服务提供商列表"""
        result = self.ai_manager.get_providers()
        
        if result.get("success"):
            providers = result.get("providers", {})
            current = result.get("current", "")
            
            console.print("[bold blue]AI服务提供商列表:[/bold blue]")
            for name, info in providers.items():
                status = "[bold green](当前)[/bold green]" if name == current else ""
                console.print(f"  {name}: {info.get('description', '')} {status}")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ai_models(self, args: List[str]) -> bool:
        """获取可用模型列表"""
        provider = args[0] if args else None
        
        result = self.ai_manager.get_models(provider)
        
        if result.get("success"):
            models = result.get("models", [])
            provider_name = result.get("provider", "")
            
            console.print(f"[bold blue]可用模型列表 ({provider_name}):[/bold blue]")
            for model in models:
                console.print(f"  {model}")
            console.print(f"[bold green]总计: {len(models)} 个模型[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ai_set(self, args: List[str]) -> bool:
        """设置AI服务提供商或模型"""
        if not args:
            console.print("[bold red]错误: 请指定操作类型[/bold red]")
            console.print("用法: ai-set <provider|model> <名称>")
            return True
            
        action = args[0]
        name = args[1] if len(args) > 1 else None
        
        if action == "provider" and name:
            result = self.ai_manager.set_provider(name)
        elif action == "model" and name:
            result = self.ai_manager.set_model(name)
        else:
            console.print("[bold red]错误: 无效的操作类型或缺少参数[/bold red]")
            console.print("用法: ai-set <provider|model> <名称>")
            return True
        
        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ai_history(self, args: List[str]) -> bool:
        """查看AI对话历史"""
        provider = args[0] if args else None
        count = int(args[1]) if len(args) > 1 else 10
        
        result = self.ai_manager.get_conversation_history(provider, count)
        
        if result.get("success"):
            history = result.get("history", [])
            provider_name = result.get("provider", "")
            
            console.print(f"[bold blue]AI对话历史 ({provider_name}):[/bold blue]")
            for i, item in enumerate(history):
                role = item.get("role", "")
                content = item.get("content", "")
                console.print(f"  {i+1}. [{role}] {content[:100]}...")
            console.print(f"[bold green]总计: {len(history)} 条记录[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ai_clear(self, args: List[str]) -> bool:
        """清除AI对话历史"""
        provider = args[0] if args else None
        
        result = self.ai_manager.clear_conversation_history(provider)
        
        if result.get("success"):
            console.print(f"[bold green]{result.get('message')}[/bold green]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        return True
    
    def cmd_ai_config(self, args: List[str]) -> bool:
        """查看或修改AI配置"""
        try:
            if not args:
                # 显示当前配置
                console.print("[bold blue]当前AI配置:[/bold blue]")
                console.print(f"  当前提供商: {self.ai_manager.current_provider}")
                console.print(f"  当前模型: {self.ai_manager.current_model}")
                console.print(f"  配置文件: {self.ai_manager.config_file}")
                return True

            action = args[0]

            if action == "show":
                # 显示完整配置
                console.print("[bold blue]AI配置详情:[/bold blue]")
                import json
                console.print(json.dumps(self.ai_manager.providers, indent=2, ensure_ascii=False))
            elif action == "edit":
                # 编辑配置
                console.print("[bold blue]编辑配置功能即将推出[/bold blue]")
            else:
                console.print("[bold red]错误: 无效的操作类型[/bold red]")
                console.print("用法: ai-config [show|edit]")
        except Exception as e:
            console.print(f"[bold red]处理AI配置时出错: {str(e)}[/bold red]")

        return True
    
    # 用户界面优化命令
    def cmd_theme(self, args: List[str]) -> bool:
        """主题管理命令"""
        if not args:
            console.print("[bold red]错误: 请指定主题操作[/bold red]")
            console.print("用法: theme <list|set|create|delete|colors> [参数]")
            return True
            
        action = args[0]
        
        if action == "list":
            # 显示主题列表
            result = self.theme_manager.get_themes()
            if result.get("success"):
                themes = result.get("themes", [])
                table = Table(title="可用主题")
                table.add_column("ID", style="cyan")
                table.add_column("名称", style="green")
                table.add_column("描述", style="blue")
                table.add_column("状态", style="yellow")
                
                for theme in themes:
                    status = "[bold green]当前[/bold green]" if theme.get("current") else ""
                    table.add_row(
                        theme["id"],
                        theme["name"],
                        theme["description"],
                        status
                    )
                
                console.print(table)
            else:
                console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        elif action == "set":
            # 设置主题
            if len(args) < 2:
                console.print("[bold red]错误: 请指定主题ID[/bold red]")
                console.print("用法: theme set <主题ID>")
                return True
                
            theme_id = args[1]
            result = self.theme_manager.set_theme(theme_id)
            
            if result.get("success"):
                console.print(f"[bold green]{result.get('message')}[/bold green]")
            else:
                console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        elif action == "create":
            # 创建新主题
            if len(args) < 2:
                console.print("[bold red]错误: 请指定主题名称[/bold red]")
                console.print("用法: theme create <主题名称> [描述]")
                return True
                
            theme_name = args[1]
            theme_description = args[2] if len(args) > 2 else "自定义主题"
            
            theme_data = {
                "id": theme_name.lower().replace(" ", "_"),
                "name": theme_name,
                "description": theme_description,
                "colors": {}
            }
            
            result = self.theme_manager.create_theme(theme_data)
            
            if result.get("success"):
                console.print(f"[bold green]{result.get('message')}[/bold green]")
            else:
                console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        elif action == "delete":
            # 删除主题
            if len(args) < 2:
                console.print("[bold red]错误: 请指定主题ID[/bold red]")
                console.print("用法: theme delete <主题ID>")
                return True
                
            theme_id = args[1]
            result = self.theme_manager.delete_theme(theme_id)
            
            if result.get("success"):
                console.print(f"[bold green]{result.get('message')}[/bold green]")
            else:
                console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        elif action == "colors":
            # 显示主题颜色
            if len(args) < 2:
                theme_id = self.theme_manager.current_theme
            else:
                theme_id = args[1]
                
            result = self.theme_manager.get_theme_colors(theme_id)
            
            if result.get("success"):
                colors = result.get("colors", {})
                console.print(f"[bold blue]主题颜色配置 ({theme_id}):[/bold blue]")
                for color_name, color_value in colors.items():
                    console.print(f"  {color_name}: {color_value}")
            else:
                console.print(f"[bold red]错误: {result.get('error')}[/bold red]")
        
        else:
            console.print(f"[bold red]错误: 未知的主题操作: {action}[/bold red]")
            console.print("用法: theme <list|set|create|delete|colors> [参数]")
        
        return True
    
    def cmd_shortcut(self, args: List[str]) -> bool:
        """快捷键管理命令 (已禁用)"""
        console.print("[bold yellow]快捷键功能已禁用以避免冲突[/bold yellow]")
        console.print("如需快捷键功能，请在应用程序级别配置")
        return True
    
    def cmd_ui(self, args: List[str]) -> bool:
        """界面增强命令"""
        if not args:
            console.print("[bold red]错误: 请指定界面操作[/bold red]")
            console.print("用法: ui <status|clear|history|help> [参数]")
            return True

        action = args[0]

        if action == "status":
            # 显示界面状态
            console.print("[bold blue]界面状态:[/bold blue]")
            console.print(f"  当前主题: {self.theme_manager.current_theme}")
            console.print(f"  历史记录: {len(self.command_history)} 条")
            console.print(f"  消息队列: {len(self.enhanced_cli.message_queue)} 条")

        elif action == "clear":
            # 清空界面
            self.enhanced_cli.clear_screen()
            console.print("[bold green]界面已清空[/bold green]")

        elif action == "history":
            # 显示历史记录
            if not self.command_history:
                console.print("[bold yellow]没有历史记录[/bold yellow]")
                return True

            count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            history = self.command_history[-count:]

            table = Table(title=f"命令历史 (最近 {count} 条)")
            table.add_column("序号", style="cyan")
            table.add_column("命令", style="green")
            table.add_column("时间", style="blue")

            for i, item in enumerate(history, 1):
                from datetime import datetime
                time_str = datetime.fromtimestamp(item["timestamp"]).strftime("%H:%M:%S")
                table.add_row(str(i), item["command"], time_str)

            console.print(table)

        elif action == "help":
            # 显示界面帮助
            help_text = """
# 界面增强功能帮助

## 主题管理:
- `theme list` - 显示主题列表
- `theme set <ID>` - 切换主题
- `theme create <名称>` - 创建新主题
- `theme delete <ID>` - 删除主题
- `theme colors [ID]` - 显示主题颜色

## 界面增强:
- `ui status` - 显示界面状态
- `ui clear` - 清空界面
- `ui history [数量]` - 显示命令历史
- `ui help` - 显示帮助
            """
            console.print(Panel(help_text, title="界面增强帮助", border_style="blue"))

        else:
            console.print(f"[bold red]错误: 未知的界面操作: {action}[/bold red]")
            console.print("用法: ui <status|clear|history|help> [参数]")

        return True
    
    # 测试和优化命令 (已移除)
    def cmd_test(self, args: List[str]) -> bool:
        """运行测试命令 (已禁用)"""
        console.print("[bold yellow]测试功能已移除以简化代码[/bold yellow]")
        return True

    def cmd_optimize(self, args: List[str]) -> bool:
        """运行优化命令 (已禁用)"""
        console.print("[bold yellow]优化功能已移除以简化代码[/bold yellow]")
        return True
    

    def cmd_mcp(self, args: List[str]) -> bool:
        """MCP相关命令"""
        if not args:
            console.print("[bold red]错误: 请指定MCP子命令[/bold red]")
            console.print("可用子命令: connect, disconnect, status")
            return True

        subcmd = args[0].lower()

        if subcmd == "connect":
            # TODO: 实现MCP连接
            console.print("[bold yellow]MCP连接功能尚未实现[/bold yellow]")
        elif subcmd == "disconnect":
            # TODO: 实现MCP断开
            console.print("[bold yellow]MCP断开功能尚未实现[/bold yellow]")
        elif subcmd == "status":
            # TODO: 实现MCP状态显示
            console.print("[bold yellow]MCP状态显示功能尚未实现[/bold yellow]")
        else:
            console.print(f"[bold red]未知MCP子命令: {subcmd}[/bold red]")

        return True

    def cmd_settings(self, args: List[str]) -> bool:
        """显示或修改设置"""
        try:
            if not args:
                # 显示当前设置
                from config.settings import DEFAULT_CONFIG
                import json

                # 获取当前设置
                current_settings = DEFAULT_CONFIG.copy()
                # TODO: 加载实际当前设置

                console.print(Panel(
                    json.dumps(current_settings, indent=2, ensure_ascii=False),
                    title="当前设置"
                ))
                return True

            action = args[0].lower()

            if action == "save":
                # TODO: 实现设置保存
                console.print("[bold yellow]设置保存功能尚未实现[/bold yellow]")
            elif action == "load":
                # TODO: 实现设置加载
                console.print("[bold yellow]设置加载功能尚未实现[/bold yellow]")
            else:
                console.print(f"[bold red]未知设置操作: {action}[/bold red]")
        except Exception as e:
            console.print(f"[bold red]处理设置时出错: {str(e)}[/bold red]")

        return True

    def _display_code_result(self, result: Dict[str, Any]) -> None:
        """显示代码执行结果"""
        if result.get("success"):
            console.print("[bold green]代码执行成功![/bold green]")

            if result.get("stdout"):
                console.print(Panel(result["stdout"], title="标准输出"))

            if result.get("stderr"):
                console.print(Panel(result["stderr"], title="标准错误", style="bold red"))

            console.print(f"[bold blue]返回码: {result.get('return_code')}[/bold blue]")
        else:
            console.print(f"[bold red]错误: {result.get('error')}[/bold red]")

    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        size_float = float(size)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_float < 1024:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024
        return f"{size_float:.1f} PB"
