#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级命令执行工具模块
提供系统命令执行和管理功能
"""

import os
import sys
import subprocess
import shlex
import threading
import time
from typing import Dict, Any, List, Optional, Union, Callable

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CommandExecutor:
    """命令执行器类"""

    def __init__(self, timeout: int = 30, allowed_commands: Optional[List[str]] = None, blocked_commands: Optional[List[str]] = None):
        """
        初始化命令执行器

        参数:
            timeout: 命令执行超时时间（秒）
            allowed_commands: 允许执行的命令列表（None表示允许所有命令）
            blocked_commands: 禁止执行的命令列表
        """
        self.timeout = timeout
        self.allowed_commands = allowed_commands
        self.blocked_commands = blocked_commands or []
        self.current_dir = os.getcwd()

        # 命令历史
        self.command_history = []
        self.max_history = 100

        # 后台任务
        self.background_tasks = {}

    def execute_command(
        self, 
        command: str, 
        timeout: Optional[int] = None,
        background: bool = False,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        shell: bool = True,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        执行系统命令

        参数:
            command: 要执行的命令
            timeout: 超时时间（秒）
            background: 是否在后台执行
            cwd: 工作目录
            env: 环境变量
            shell: 是否使用shell执行
            callback: 执行完成后的回调函数

        返回:
            执行结果
        """
        # 检查命令是否被允许
        if not self._is_command_allowed(command):
            return {"error": "命令被禁止执行"}

        # 设置默认值
        timeout = timeout or self.timeout
        cwd = cwd or self.current_dir

        # 记录命令历史
        self._add_to_history(command)

        try:
            logger.info(f"执行命令: {command}")

            if background:
                # 后台执行
                return self._execute_background(
                    command, timeout, cwd, env, shell, callback
                )
            else:
                # 前台执行
                return self._execute_foreground(
                    command, timeout, cwd, env, shell
                )
        except Exception as e:
            error_msg = f"命令执行失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _execute_foreground(
        self, 
        command: str, 
        timeout: int, 
        cwd: str, 
        env: Optional[Dict[str, str]], 
        shell: bool
    ) -> Dict[str, Any]:
        """
        前台执行命令

        参数:
            command: 要执行的命令
            timeout: 超时时间
            cwd: 工作目录
            env: 环境变量
            shell: 是否使用shell执行

        返回:
            执行结果
        """
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env or os.environ
            )

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command,
                "timeout": timeout,
                "background": False
            }
        except subprocess.TimeoutExpired:
            error_msg = f"命令执行超时: {timeout}秒"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"命令执行失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _execute_background(
        self, 
        command: str, 
        timeout: int, 
        cwd: str, 
        env: Optional[Dict[str, str]], 
        shell: bool,
        callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        后台执行命令

        参数:
            command: 要执行的命令
            timeout: 超时时间
            cwd: 工作目录
            env: 环境变量
            shell: 是否使用shell执行
            callback: 执行完成后的回调函数

        返回:
            执行结果
        """
        try:
            # 生成任务ID
            task_id = f"bg_{int(time.time() * 1000000)}"

            # 创建后台任务
            task = {
                "id": task_id,
                "command": command,
                "start_time": time.time(),
                "timeout": timeout,
                "cwd": cwd,
                "env": env or os.environ,
                "shell": shell,
                "running": True,
                "result": None,
                "process": None,
                "callback": callback
            }

            # 启动执行线程
            thread = threading.Thread(
                target=self._execute_background_task,
                args=(task,)
            )
            thread.daemon = True
            thread.start()

            # 保存任务
            self.background_tasks[task_id] = task

            logger.info(f"启动后台任务: {task_id} - {command}")

            return {
                "success": True,
                "task_id": task_id,
                "command": command,
                "timeout": timeout,
                "background": True
            }
        except Exception as e:
            error_msg = f"后台任务启动失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _execute_background_task(self, task: Dict[str, Any]) -> None:
        """
        执行后台任务

        参数:
            task: 任务信息
        """
        try:
            # 启动进程
            process = subprocess.Popen(
                task["command"],
                shell=task["shell"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=task["cwd"],
                env=task["env"]
            )

            task["process"] = process

            # 等待完成或超时
            start_time = time.time()
            while time.time() - start_time < task["timeout"]:
                if process.poll() is not None:
                    # 进程已结束
                    break

                time.sleep(0.1)

            # 检查是否超时
            if process.poll() is None:
                # 超时，终止进程
                process.terminate()
                process.wait(timeout=5)

            # 获取结果
            stdout, stderr = process.communicate()

            task["result"] = {
                "success": True,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": process.returncode,
                "command": task["command"],
                "timeout": task["timeout"],
                "background": True
            }

            task["running"] = False

            # 调用回调函数
            if task["callback"]:
                task["callback"](task["result"])

            logger.info(f"后台任务完成: {task['id']} - {task['command']}")
        except Exception as e:
            error_msg = f"后台任务执行失败: {str(e)}"
            logger.error(error_msg)

            task["result"] = {"error": error_msg}
            task["running"] = False

            # 调用回调函数
            if task["callback"]:
                task["callback"]({"error": error_msg})

    def get_background_tasks(self) -> Dict[str, Any]:
        """
        获取所有后台任务

        返回:
            后台任务列表
        """
        tasks = {}

        for task_id, task in self.background_tasks.items():
            tasks[task_id] = {
                "id": task["id"],
                "command": task["command"],
                "start_time": task["start_time"],
                "running": task["running"],
                "result": task["result"]
            }

        return tasks

    def get_background_task(self, task_id: str) -> Dict[str, Any]:
        """
        获取指定后台任务

        参数:
            task_id: 任务ID

        返回:
            任务信息
        """
        if task_id not in self.background_tasks:
            return {"error": f"任务不存在: {task_id}"}

        task = self.background_tasks[task_id]

        return {
            "id": task["id"],
            "command": task["command"],
            "start_time": task["start_time"],
            "running": task["running"],
            "result": task["result"]
        }

    def stop_background_task(self, task_id: str) -> Dict[str, Any]:
        """
        停止后台任务

        参数:
            task_id: 任务ID

        返回:
            操作结果
        """
        if task_id not in self.background_tasks:
            return {"error": f"任务不存在: {task_id}"}

        task = self.background_tasks[task_id]

        if not task["running"]:
            return {"error": f"任务未运行: {task_id}"}

        try:
            # 终止进程
            if task["process"]:
                task["process"].terminate()
                task["process"].wait(timeout=5)

            task["running"] = False

            logger.info(f"停止后台任务: {task_id} - {task['command']}")

            return {
                "success": True,
                "message": f"已停止后台任务: {task_id}"
            }
        except Exception as e:
            error_msg = f"停止后台任务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def clear_background_tasks(self) -> Dict[str, Any]:
        """
        清除所有已完成的后台任务

        返回:
            操作结果
        """
        cleared_tasks = []

        for task_id, task in list(self.background_tasks.items()):
            if not task["running"]:
                cleared_tasks.append(task_id)
                del self.background_tasks[task_id]

        logger.info(f"清除后台任务: {len(cleared_tasks)} 个")

        return {
            "success": True,
            "cleared_tasks": cleared_tasks,
            "count": len(cleared_tasks)
        }

    def _is_command_allowed(self, command: str) -> bool:
        """
        检查命令是否被允许执行

        参数:
            command: 要检查的命令

        返回:
            是否允许执行
        """
        # 如果有允许列表，只允许列表中的命令
        if self.allowed_commands:
            # 检查命令是否在允许列表中
            allowed = False
            for allowed_cmd in self.allowed_commands:
                if command.strip().startswith(allowed_cmd):
                    allowed = True
                    break

            if not allowed:
                logger.warning(f"命令不在允许列表中: {command}")
                return False

        # 检查是否在禁止列表中
        for blocked_cmd in self.blocked_commands:
            if command.strip().lower().startswith(blocked_cmd.lower()):
                logger.warning(f"命令被禁止执行: {command}")
                return False

        return True

    def _add_to_history(self, command: str) -> None:
        """
        添加命令到历史记录

        参数:
            command: 命令
        """
        self.command_history.append({
            "command": command,
            "time": time.time(),
            "cwd": self.current_dir
        })

        # 限制历史记录长度
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)

    def get_command_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        获取命令历史

        参数:
            count: 返回的历史记录数量

        返回:
            命令历史记录
        """
        return self.command_history[-count:]

    def clear_command_history(self) -> Dict[str, Any]:
        """
        清除命令历史

        返回:
            操作结果
        """
        count = len(self.command_history)
        self.command_history = []

        logger.info(f"清除命令历史: {count} 条")

        return {
            "success": True,
            "cleared_count": count
        }

    def set_current_dir(self, path: str) -> Dict[str, Any]:
        """
        设置当前工作目录

        参数:
            path: 目录路径

        返回:
            操作结果
        """
        try:
            abs_path = os.path.abspath(path)

            if not os.path.exists(abs_path):
                return {"error": f"路径不存在: {abs_path}"}

            if not os.path.isdir(abs_path):
                return {"error": f"路径不是目录: {abs_path}"}

            self.current_dir = abs_path

            logger.info(f"设置当前目录: {abs_path}")

            return {
                "success": True,
                "message": f"已设置当前目录: {abs_path}",
                "path": abs_path
            }
        except Exception as e:
            error_msg = f"设置当前目录失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_current_dir(self) -> str:
        """
        获取当前工作目录

        返回:
            当前工作目录
        """
        return self.current_dir

    def batch_execute(
        self, 
        commands: List[str], 
        timeout: Optional[int] = None,
        continue_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        批量执行命令

        参数:
            commands: 命令列表
            timeout: 每个命令的超时时间
            continue_on_error: 是否在出错时继续执行

        返回:
            执行结果
        """
        results = []
        success_count = 0
        error_count = 0

        for i, command in enumerate(commands):
            logger.info(f"批量执行命令 {i+1}/{len(commands)}: {command}")

            result = self.execute_command(command, timeout)
            results.append(result)

            if result.get("success"):
                success_count += 1
            else:
                error_count += 1
                if not continue_on_error:
                    break

        return {
            "success": error_count == 0,
            "results": results,
            "total": len(commands),
            "success_count": success_count,
            "error_count": error_count,
            "commands": commands
        }

    def execute_script(
        self, 
        script: str, 
        interpreter: str = "python",
        timeout: Optional[int] = None,
        args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        执行脚本

        参数:
            script: 脚本内容
            interpreter: 解释器
            timeout: 超时时间
            args: 脚本参数

        返回:
            执行结果
        """
        try:
            # 创建临时脚本文件
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=f'.{interpreter.split(".")[-1] if "." in interpreter else interpreter}',
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(script)
                temp_file_path = temp_file.name

            # 构建执行命令
            if args:
                command = f"{interpreter} {temp_file_path} {' '.join(args)}"
            else:
                command = f"{interpreter} {temp_file_path}"

            # 执行命令
            result = self.execute_command(command, timeout)

            # 清理临时文件
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

            return result
        except Exception as e:
            error_msg = f"执行脚本失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
