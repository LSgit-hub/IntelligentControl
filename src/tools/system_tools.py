#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统工具模块
提供系统操作相关的功能
"""

import os
import sys
import subprocess
import shutil
import winreg
import ctypes
from typing import Dict, Any, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SystemTools:
    """系统工具类"""

    def __init__(self):
        """初始化系统工具"""
        self.current_dir = os.getcwd()

    def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        执行系统命令

        参数:
            command: 要执行的命令
            timeout: 超时时间（秒）

        返回:
            包含执行结果的字典
        """
        try:
            logger.info(f"执行命令: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.current_dir
            )

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            error_msg = f"命令执行超时: {timeout}秒"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"命令执行失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def list_files(self, path: str = ".") -> Dict[str, Any]:
        """
        列出指定目录中的文件

        参数:
            path: 目录路径

        返回:
            包含文件列表的字典
        """
        try:
            abs_path = os.path.abspath(path)
            if not os.path.exists(abs_path):
                return {"error": f"路径不存在: {abs_path}"}

            if not os.path.isdir(abs_path):
                return {"error": f"路径不是目录: {abs_path}"}

            files = os.listdir(abs_path)
            file_info = []

            for file in files:
                full_path = os.path.join(abs_path, file)
                file_info.append({
                    "name": file,
                    "path": full_path,
                    "is_dir": os.path.isdir(full_path),
                    "size": os.path.getsize(full_path) if not os.path.isdir(full_path) else 0,
                    "modified": os.path.getmtime(full_path)
                })

            return {"success": True, "files": file_info, "path": abs_path}
        except Exception as e:
            error_msg = f"列出文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def create_directory(self, path: str) -> Dict[str, Any]:
        """
        创建目录

        参数:
            path: 目录路径

        返回:
            操作结果
        """
        try:
            abs_path = os.path.abspath(path)
            os.makedirs(abs_path, exist_ok=True)

            logger.info(f"创建目录: {abs_path}")
            return {"success": True, "message": f"目录已创建: {abs_path}"}
        except Exception as e:
            error_msg = f"创建目录失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def create_file(self, path: str, content: str = "") -> Dict[str, Any]:
        """
        创建文件

        参数:
            path: 文件路径
            content: 文件内容

        返回:
            操作结果
        """
        try:
            abs_path = os.path.abspath(path)

            # 确保目录存在
            dir_path = os.path.dirname(abs_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            with open(abs_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"创建文件: {abs_path}")
            return {"success": True, "message": f"文件已创建: {abs_path}"}
        except Exception as e:
            error_msg = f"创建文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def read_file(self, path: str) -> Dict[str, Any]:
        """
        读取文件内容

        参数:
            path: 文件路径

        返回:
            包含文件内容的字典
        """
        try:
            abs_path = os.path.abspath(path)

            if not os.path.exists(abs_path):
                return {"error": f"文件不存在: {abs_path}"}

            if not os.path.isfile(abs_path):
                return {"error": f"路径不是文件: {abs_path}"}

            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {"success": True, "content": content, "path": abs_path}
        except Exception as e:
            error_msg = f"读取文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def write_file(self, path: str, content: str, append: bool = False) -> Dict[str, Any]:
        """
        写入文件内容

        参数:
            path: 文件路径
            content: 要写入的内容
            append: 是否追加模式

        返回:
            操作结果
        """
        try:
            abs_path = os.path.abspath(path)

            # 确保目录存在
            dir_path = os.path.dirname(abs_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            mode = 'a' if append else 'w'
            with open(abs_path, mode, encoding='utf-8') as f:
                f.write(content)

            action = "追加到" if append else "写入"
            logger.info(f"{action}文件: {abs_path}")
            return {"success": True, "message": f"内容已{action}: {abs_path}"}
        except Exception as e:
            error_msg = f"写入文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def delete_file(self, path: str) -> Dict[str, Any]:
        """
        删除文件或目录

        参数:
            path: 文件或目录路径

        返回:
            操作结果
        """
        try:
            abs_path = os.path.abspath(path)

            if not os.path.exists(abs_path):
                return {"error": f"路径不存在: {abs_path}"}

            if os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
                logger.info(f"删除目录: {abs_path}")
                return {"success": True, "message": f"目录已删除: {abs_path}"}
            else:
                os.remove(abs_path)
                logger.info(f"删除文件: {abs_path}")
                return {"success": True, "message": f"文件已删除: {abs_path}"}
        except Exception as e:
            error_msg = f"删除失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息

        返回:
            包含系统信息的字典
        """
        try:
            import platform

            info = {
                "os": os.name,
                "platform": sys.platform,
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "user": os.getenv('USERNAME'),
                "computer": os.getenv('COMPUTERNAME'),
                "home": os.path.expanduser('~'),
                "current_dir": os.getcwd()
            }

            return {"success": True, "info": info}
        except Exception as e:
            error_msg = f"获取系统信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_environment_variable(self, name: str) -> Dict[str, Any]:
        """
        获取环境变量

        参数:
            name: 环境变量名

        返回:
            包含环境变量值的字典
        """
        try:
            value = os.getenv(name)
            if value is None:
                return {"error": f"环境变量不存在: {name}"}

            return {"success": True, "name": name, "value": value}
        except Exception as e:
            error_msg = f"获取环境变量失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def set_environment_variable(self, name: str, value: str, persistent: bool = False) -> Dict[str, Any]:
        """
        设置环境变量

        参数:
            name: 环境变量名
            value: 环境变量值
            persistent: 是否持久化（Windows注册表）

        返回:
            操作结果
        """
        try:
            os.environ[name] = value

            if persistent and os.name == 'nt':
                # 设置为系统环境变量（Windows）
                try:
                    import winreg
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        "SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                        0,
                        winreg.KEY_ALL_ACCESS
                    )
                    winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
                    winreg.CloseKey(key)

                    # 通知系统环境变量已更改
                    ctypes.windll.user32.SendMessageTimeoutW(
                        0xFFFF, 0x001A, 0, "Environment", 0x0002, 5000, None
                    )

                    logger.info(f"持久化设置环境变量: {name}={value}")
                except Exception as e:
                    logger.warning(f"无法持久化环境变量: {str(e)}")

            logger.info(f"设置环境变量: {name}={value}")
            return {"success": True, "message": f"环境变量已设置: {name}={value}"}
        except Exception as e:
            error_msg = f"设置环境变量失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def run_as_admin(self, command: str) -> Dict[str, Any]:
        """
        以管理员权限运行命令

        参数:
            command: 要运行的命令

        返回:
            执行结果
        """
        try:
            # 检查是否具有管理员权限
            if not ctypes.windll.shell32.IsUserAnAdmin():
                return {"error": "需要管理员权限"}

            logger.info(f"以管理员权限运行命令: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            error_msg = "命令执行超时"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"命令执行失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
