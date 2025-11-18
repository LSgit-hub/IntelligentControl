#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
进程管理工具模块
提供进程管理功能
"""

import os
import sys
import psutil
import signal
import subprocess
import time
from typing import Dict, Any, List, Optional, Union

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ProcessManager:
    """进程管理器类"""

    def __init__(self):
        """初始化进程管理器"""
        self.current_dir = os.getcwd()

    def list_processes(self, detailed: bool = False, filter_name: Optional[str] = None) -> Dict[str, Any]:
        """
        列出系统进程

        参数:
            detailed: 是否显示详细信息
            filter_name: 进程名称过滤器

        返回:
            进程列表
        """
        try:
            processes = []

            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info

                    # 应用过滤器
                    if filter_name and filter_name.lower() not in proc_info['name'].lower():
                        continue

                    if detailed:
                        # 获取更详细的信息
                        try:
                            proc_info['cmdline'] = proc.cmdline()
                            proc_info['cwd'] = proc.cwd()
                            proc_info['create_time'] = proc.create_time()
                            proc_info['memory_info'] = proc.memory_info()._asdict()
                            proc_info['num_threads'] = proc.num_threads()
                            proc_info['connections'] = [conn._asdict() for conn in proc.connections()]
                            proc_info['open_files'] = [file.path for file in proc.open_files()]
                        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                            pass

                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

            # 按CPU使用率排序
            processes.sort(key=lambda p: p.get('cpu_percent', 0), reverse=True)

            logger.info(f"列出进程: 找到 {len(processes)} 个进程")

            return {
                "success": True,
                "processes": processes,
                "count": len(processes),
                "filter_name": filter_name
            }
        except Exception as e:
            error_msg = f"列出进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_process_info(self, pid: int) -> Dict[str, Any]:
        """
        获取指定进程的详细信息

        参数:
            pid: 进程ID

        返回:
            进程信息
        """
        try:
            proc = psutil.Process(pid)

            proc_info = {
                "pid": pid,
                "name": proc.name(),
                "status": proc.status(),
                "username": proc.username(),
                "cpu_percent": proc.cpu_percent(),
                "memory_percent": proc.memory_percent(),
                "cmdline": proc.cmdline(),
                "cwd": proc.cwd(),
                "create_time": proc.create_time(),
                "memory_info": proc.memory_info()._asdict(),
                "num_threads": proc.num_threads(),
                "connections": [conn._asdict() for conn in proc.connections()],
                "open_files": [file.path for file in proc.open_files()],
                "children": [child.pid for child in proc.children()]
            }

            logger.info(f"获取进程信息: {pid} - {proc_info['name']}")

            return {
                "success": True,
                "process": proc_info
            }
        except psutil.NoSuchProcess:
            error_msg = f"进程不存在: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except psutil.AccessDenied:
            error_msg = f"无权限访问进程: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"获取进程信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def kill_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """
        终止进程

        参数:
            pid: 进程ID
            force: 是否强制终止

        返回:
            操作结果
        """
        try:
            proc = psutil.Process(pid)

            if force:
                proc.kill()
                logger.info(f"强制终止进程: {pid} - {proc.name()}")
            else:
                proc.terminate()
                logger.info(f"终止进程: {pid} - {proc.name()}")

            return {
                "success": True,
                "message": f"已终止进程: {pid}",
                "name": proc.name(),
                "force": force
            }
        except psutil.NoSuchProcess:
            error_msg = f"进程不存在: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except psutil.AccessDenied:
            error_msg = f"无权限终止进程: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"终止进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def suspend_process(self, pid: int) -> Dict[str, Any]:
        """
        暂停进程

        参数:
            pid: 进程ID

        返回:
            操作结果
        """
        try:
            proc = psutil.Process(pid)

            if sys.platform == 'win32':
                # Windows系统
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(0x1F0000, False, pid)
                if handle == 0:
                    error_msg = f"无法打开进程句柄: {pid}"
                    logger.error(error_msg)
                    return {"error": error_msg}

                ctypes.windll.ntdll.NtSuspendProcess(handle)
                kernel32.CloseHandle(handle)
            else:
                # Unix-like系统
                proc.suspend()

            logger.info(f"暂停进程: {pid} - {proc.name()}")

            return {
                "success": True,
                "message": f"已暂停进程: {pid}",
                "name": proc.name()
            }
        except psutil.NoSuchProcess:
            error_msg = f"进程不存在: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except psutil.AccessDenied:
            error_msg = f"无权限暂停进程: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"暂停进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def resume_process(self, pid: int) -> Dict[str, Any]:
        """
        恢复进程

        参数:
            pid: 进程ID

        返回:
            操作结果
        """
        try:
            proc = psutil.Process(pid)

            if sys.platform == 'win32':
                # Windows系统
                import ctypes
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(0x1F0000, False, pid)
                if handle == 0:
                    error_msg = f"无法打开进程句柄: {pid}"
                    logger.error(error_msg)
                    return {"error": error_msg}

                ctypes.windll.ntdll.NtResumeProcess(handle)
                kernel32.CloseHandle(handle)
            else:
                # Unix-like系统
                proc.resume()

            logger.info(f"恢复进程: {pid} - {proc.name()}")

            return {
                "success": True,
                "message": f"已恢复进程: {pid}",
                "name": proc.name()
            }
        except psutil.NoSuchProcess:
            error_msg = f"进程不存在: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except psutil.AccessDenied:
            error_msg = f"无权限恢复进程: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"恢复进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def create_process(
        self, 
        command: str, 
        cwd: Optional[str] = None, 
        env: Optional[Dict[str, str]] = None,
        shell: bool = True,
        stdout: bool = True,
        stderr: bool = True
    ) -> Dict[str, Any]:
        """
        创建新进程

        参数:
            command: 要执行的命令
            cwd: 工作目录
            env: 环境变量
            shell: 是否使用shell执行
            stdout: 是否捕获标准输出
            stderr: 是否捕获标准错误

        返回:
            进程信息
        """
        try:
            # 设置默认工作目录
            if cwd is None:
                cwd = self.current_dir

            # 设置默认环境变量
            if env is None:
                env = os.environ.copy()

            # 创建进程
            if stdout and stderr:
                proc = subprocess.Popen(
                    command,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif stdout:
                proc = subprocess.Popen(
                    command,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
            elif stderr:
                proc = subprocess.Popen(
                    command,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                proc = subprocess.Popen(
                    command,
                    shell=shell,
                    cwd=cwd,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    text=True
                )

            logger.info(f"创建进程: {command} (PID: {proc.pid})")

            return {
                "success": True,
                "pid": proc.pid,
                "command": command,
                "cwd": cwd,
                "shell": shell,
                "stdout": stdout,
                "stderr": stderr
            }
        except Exception as e:
            error_msg = f"创建进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_process_children(self, pid: int) -> Dict[str, Any]:
        """
        获取子进程列表

        参数:
            pid: 父进程ID

        返回:
            子进程列表
        """
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)

            children_info = []
            for child in children:
                try:
                    child_info = {
                        "pid": child.pid,
                        "name": child.name(),
                        "status": child.status(),
                        "cpu_percent": child.cpu_percent(),
                        "memory_percent": child.memory_percent(),
                        "cmdline": child.cmdline()
                    }
                    children_info.append(child_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            logger.info(f"获取子进程: {pid} - 找到 {len(children_info)} 个子进程")

            return {
                "success": True,
                "pid": pid,
                "children": children_info,
                "count": len(children_info)
            }
        except psutil.NoSuchProcess:
            error_msg = f"进程不存在: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except psutil.AccessDenied:
            error_msg = f"无权限访问进程: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"获取子进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def monitor_process(self, pid: int, interval: float = 1.0, duration: Optional[float] = None) -> Dict[str, Any]:
        """
        监控进程

        参数:
            pid: 进程ID
            interval: 采样间隔（秒）
            duration: 监控持续时间（秒），None表示无限监控

        返回:
            监控结果
        """
        try:
            proc = psutil.Process(pid)

            start_time = time.time()
            samples = []

            while True:
                try:
                    # 获取进程信息
                    sample = {
                        "timestamp": time.time(),
                        "cpu_percent": proc.cpu_percent(),
                        "memory_percent": proc.memory_percent(),
                        "memory_info": proc.memory_info()._asdict(),
                        "num_threads": proc.num_threads(),
                        "status": proc.status()
                    }

                    samples.append(sample)

                    logger.debug(f"监控进程: {pid} - CPU: {sample['cpu_percent']}%, 内存: {sample['memory_percent']}%")

                    # 检查是否超时
                    if duration and (time.time() - start_time) >= duration:
                        break

                    # 等待下一次采样
                    time.sleep(interval)

                except psutil.NoSuchProcess:
                    logger.warning(f"进程已终止: {pid}")
                    break
                except psutil.AccessDenied:
                    logger.warning(f"无权限访问进程: {pid}")
                    break

            logger.info(f"监控进程完成: {pid} - 采集 {len(samples)} 个样本")

            return {
                "success": True,
                "pid": pid,
                "interval": interval,
                "duration": duration,
                "samples": samples,
                "count": len(samples)
            }
        except psutil.NoSuchProcess:
            error_msg = f"进程不存在: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except psutil.AccessDenied:
            error_msg = f"无权限访问进程: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"监控进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
