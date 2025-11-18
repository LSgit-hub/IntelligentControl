#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高级系统信息获取工具模块
提供系统信息获取功能
"""

import os
import sys
import platform
import psutil
import socket
import uuid
import time
from typing import Dict, Any, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class SystemInfo:
    """系统信息获取器类"""

    def __init__(self):
        """初始化系统信息获取器"""
        self.system = platform.system().lower()
        self.current_dir = os.getcwd()

    def get_basic_info(self) -> Dict[str, Any]:
        """
        获取基本系统信息

        返回:
            基本系统信息
        """
        try:
            info = {
                "system": {
                    "name": platform.system(),
                    "version": platform.version(),
                    "release": platform.release(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "node": platform.node(),
                    "python_version": platform.python_version(),
                    "python_implementation": platform.python_implementation(),
                    "python_build": platform.python_build(),
                    "python_compiler": platform.python_compiler(),
                    "python_branch": platform.python_branch(),
                    "python_revision": platform.python_revision(),
                    "python_serial": platform.python_serial()
                },
                "time": {
                    "timestamp": time.time(),
                    "localtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    "timezone": time.tzname[0]
                },
                "network": {
                    "hostname": socket.gethostname(),
                    "fqdn": socket.getfqdn(),
                    "ip_address": socket.gethostbyname(socket.gethostname())
                },
                "system_paths": {
                    "current_dir": os.getcwd(),
                    "home_dir": os.path.expanduser("~"),
                    "temp_dir": os.path.expanduser("~/AppData/Local/Temp") if self.system == "windows" else "/tmp"
                }
            }

            logger.info("获取基本系统信息成功")
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            error_msg = f"获取基本系统信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_hardware_info(self) -> Dict[str, Any]:
        """
        获取硬件信息

        返回:
            硬件信息
        """
        try:
            info = {
                "cpu": {
                    "count": psutil.cpu_count(logical=False),
                    "logical_count": psutil.cpu_count(logical=True),
                    "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
                    "usage_percent": psutil.cpu_percent(interval=1),
                    "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used,
                    "free": psutil.virtual_memory().free,
                    "swap_total": psutil.swap_memory().total,
                    "swap_used": psutil.swap_memory().used,
                    "swap_percent": psutil.swap_memory().percent
                },
                "disk": {
                    "partitions": [],
                    "io_counters": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None
                },
                "network": {
                    "interfaces": psutil.net_if_addrs(),
                    "io_counters": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
                }
            }

            # 获取磁盘分区信息
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partition_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "opts": partition.opts,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                    info["disk"]["partitions"].append(partition_info)
                except Exception:
                    continue

            logger.info("获取硬件信息成功")
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            error_msg = f"获取硬件信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_users_info(self) -> Dict[str, Any]:
        """
        获取用户信息

        返回:
            用户信息
        """
        try:
            info = {
                "current_user": {
                    "name": os.getenv("USERNAME") if self.system == "windows" else os.getenv("USER"),
                    "home": os.path.expanduser("~"),
                    "id": os.getuid() if hasattr(os, "getuid") else None,
                    "groups": os.getgroups() if hasattr(os, "getgroups") else None
                },
                "users": [],
                "logged_in_users": []
            }

            # 获取所有用户信息
            if self.system == "windows":
                # Windows系统
                import winreg

                try:
                    # 从注册表获取用户信息
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList")
                    i = 0
                    while True:
                        try:
                            sid = winreg.EnumKey(key, i)
                            user_key = winreg.OpenKey(key, sid)
                            profile_path = winreg.QueryValueEx(user_key, "ProfileImagePath")[0]
                            username = os.path.basename(profile_path)

                            user_info = {
                                "name": username,
                                "sid": sid,
                                "path": profile_path,
                                "home": profile_path
                            }
                            info["users"].append(user_info)
                            i += 1
                        except WindowsError:
                            break
                except Exception as e:
                    logger.warning(f"无法从注册表获取用户信息: {str(e)}")

                # 获取当前登录用户
                import ctypes
                import getpass

                try:
                    username = getpass.getuser()
                    info["current_user"]["name"] = username

                    # 获取用户SID
                    import win32security
                    import win32api

                    domain, username = username.split("\\") if "\\" in username else (None, username)
                    sid, _, _ = win32security.LookupAccountName(domain, username)
                    info["current_user"]["sid"] = win32security.ConvertSidToStringSid(sid)
                except Exception as e:
                    logger.warning(f"无法获取当前用户SID: {str(e)}")
            else:
                # Unix-like系统
                import pwd

                # 获取所有用户
                for user in pwd.getpwall():
                    user_info = {
                        "name": user.pw_name,
                        "uid": user.pw_uid,
                        "gid": user.pw_gid,
                        "home": user.pw_dir,
                        "shell": user.pw_shell,
                        "gecos": user.pw_gecos
                    }
                    info["users"].append(user_info)

                # 获取当前登录用户
                info["current_user"]["name"] = os.getenv("USER")
                info["current_user"]["uid"] = os.getuid()
                info["current_user"]["gid"] = os.getgid()

            # 获取当前登录用户
            for user in psutil.users():
                user_info = {
                    "name": user.name,
                    "terminal": user.terminal,
                    "host": user.host,
                    "started": user.started,
                    "pid": user.pid
                }
                info["logged_in_users"].append(user_info)

            logger.info("获取用户信息成功")
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            error_msg = f"获取用户信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_environment_variables(self) -> Dict[str, Any]:
        """
        获取环境变量

        返回:
            环境变量
        """
        try:
            info = {
                "variables": dict(os.environ),
                "count": len(os.environ)
            }

            logger.info("获取环境变量成功")
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            error_msg = f"获取环境变量失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_network_info(self) -> Dict[str, Any]:
        """
        获取网络信息

        返回:
            网络信息
        """
        try:
            info = {
                "interfaces": {},
                "connections": [],
                "io_counters": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None,
                "addresses": {}
            }

            # 获取网络接口信息
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                info["interfaces"][interface_name] = []

                for address in interface_addresses:
                    address_info = {
                        "family": str(address.family),
                        "address": address.address,
                        "netmask": address.netmask,
                        "broadcast": address.broadcast
                    }
                    info["interfaces"][interface_name].append(address_info)

            # 获取网络连接信息
            for conn in psutil.net_connections():
                conn_info = {
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    "status": conn.status,
                    "pid": conn.pid
                }
                info["connections"].append(conn_info)

            logger.info("获取网络信息成功")
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            error_msg = f"获取网络信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_processes_summary(self) -> Dict[str, Any]:
        """
        获取进程摘要信息

        返回:
            进程摘要信息
        """
        try:
            processes = list(psutil.process_iter())

            # 统计进程信息
            total_processes = len(processes)
            running_processes = 0
            sleeping_processes = 0
            stopped_processes = 0
            zombie_processes = 0

            total_cpu = 0
            total_memory = 0
            top_processes = []

            for proc in processes:
                try:
                    proc_info = proc.as_dict(attrs=[
                        "pid", "name", "status", "cpu_percent", "memory_percent", "create_time"
                    ])

                    # 统计状态
                    status = proc_info["status"]
                    if status == "running":
                        running_processes += 1
                    elif status == "sleeping":
                        sleeping_processes += 1
                    elif status == "stopped":
                        stopped_processes += 1
                    elif status == "zombie":
                        zombie_processes += 1

                    # 累加CPU和内存使用
                    total_cpu += proc_info["cpu_percent"]
                    total_memory += proc_info["memory_percent"]

                    # 记录TOP进程
                    top_processes.append({
                        "pid": proc_info["pid"],
                        "name": proc_info["name"],
                        "cpu_percent": proc_info["cpu_percent"],
                        "memory_percent": proc_info["memory_percent"],
                        "status": proc_info["status"]
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 按CPU使用率排序TOP进程
            top_processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            top_processes = top_processes[:10]  # 只取前10个

            info = {
                "summary": {
                    "total_processes": total_processes,
                    "running_processes": running_processes,
                    "sleeping_processes": sleeping_processes,
                    "stopped_processes": stopped_processes,
                    "zombie_processes": zombie_processes,
                    "total_cpu_percent": total_cpu,
                    "total_memory_percent": total_memory
                },
                "top_processes": top_processes
            }

            logger.info("获取进程摘要信息成功")
            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            error_msg = f"获取进程摘要信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_system_summary(self) -> Dict[str, Any]:
        """
        获取系统摘要信息

        返回:
            系统摘要信息
        """
        try:
            # 获取基本信息
            basic_info = self.get_basic_info()
            if not basic_info.get("success"):
                return basic_info

            # 获取硬件信息
            hardware_info = self.get_hardware_info()
            if not hardware_info.get("success"):
                return hardware_info

            # 获取用户信息
            users_info = self.get_users_info()
            if not users_info.get("success"):
                return users_info

            # 获取网络信息
            network_info = self.get_network_info()
            if not network_info.get("success"):
                return network_info

            # 获取进程摘要
            processes_summary = self.get_processes_summary()
            if not processes_summary.get("success"):
                return processes_summary

            # 组合摘要信息
            summary = {
                "basic": basic_info["info"],
                "hardware": hardware_info["info"],
                "users": users_info["info"],
                "network": network_info["info"],
                "processes": processes_summary["info"]
            }

            logger.info("获取系统摘要信息成功")
            return {
                "success": True,
                "info": summary
            }
        except Exception as e:
            error_msg = f"获取系统摘要信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
