#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统服务管理工具模块
提供系统服务管理功能
"""

import os
import sys
import subprocess
import platform
from typing import Dict, Any, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ServiceManager:
    """系统服务管理器类"""

    def __init__(self):
        """初始化系统服务管理器"""
        self.system = platform.system().lower()
        self.current_dir = os.getcwd()

    def list_services(self, detailed: bool = False) -> Dict[str, Any]:
        """
        列出系统服务

        参数:
            detailed: 是否显示详细信息

        返回:
            服务列表
        """
        try:
            if self.system == 'windows':
                return self._list_windows_services(detailed)
            elif self.system in ['linux', 'darwin']:
                return self._list_unix_services(detailed)
            else:
                return {"error": f"不支持的系统: {self.system}"}
        except Exception as e:
            error_msg = f"列出服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _list_windows_services(self, detailed: bool) -> Dict[str, Any]:
        """
        列出Windows系统服务

        参数:
            detailed: 是否显示详细信息

        返回:
            服务列表
        """
        try:
            # 使用sc命令获取服务列表
            result = subprocess.run(
                ["sc", "query", "state=", "all"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {"error": f"获取服务列表失败: {result.stderr}"}

            # 解析服务列表
            services = []
            current_service = {}

            for line in result.stdout.split('\n'):
                if not line:
                    if current_service:
                        services.append(current_service)
                        current_service = {}
                    continue

                if line.startswith("SERVICE_NAME:"):
                    if current_service:
                        services.append(current_service)
                    current_service = {
                        "name": line.split(":", 1)[1].strip(),
                        "state": "",
                        "type": "",
                        "win32_exit_code": "",
                        "service_exit_code": "",
                        "checkpoint": "",
                        "wait_hint": "",
                        "process_id": ""
                    }
                elif line.startswith("STATE:"):
                    current_service["state"] = line.split(":", 1)[1].strip()
                elif line.startswith("TYPE:"):
                    current_service["type"] = line.split(":", 1)[1].strip()
                elif line.startswith("WIN32_EXIT_CODE:"):
                    current_service["win32_exit_code"] = line.split(":", 1)[1].strip()
                elif line.startswith("SERVICE_EXIT_CODE:"):
                    current_service["service_exit_code"] = line.split(":", 1)[1].strip()
                elif line.startswith("CHECKPOINT:"):
                    current_service["checkpoint"] = line.split(":", 1)[1].strip()
                elif line.startswith("WAIT_HINT:"):
                    current_service["wait_hint"] = line.split(":", 1)[1].strip()
                elif line.startswith("PID:"):
                    current_service["process_id"] = line.split(":", 1)[1].strip()

            # 添加最后一个服务
            if current_service:
                services.append(current_service)

            # 如果需要详细信息，获取每个服务的更多信息
            if detailed:
                detailed_services = []
                for service in services:
                    name = service["name"]
                    detailed_info = self._get_windows_service_info(name)
                    if detailed_info.get("success"):
                        service.update(detailed_info.get("service", {}))
                    detailed_services.append(service)
                services = detailed_services

            logger.info(f"列出Windows服务: 找到 {len(services)} 个服务")

            return {
                "success": True,
                "services": services,
                "count": len(services),
                "system": self.system
            }
        except Exception as e:
            error_msg = f"列出Windows服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _list_unix_services(self, detailed: bool) -> Dict[str, Any]:
        """
        列出Unix系统服务

        参数:
            detailed: 是否显示详细信息

        返回:
            服务列表
        """
        try:
            # 使用systemctl命令获取服务列表
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service", "--all"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {"error": f"获取服务列表失败: {result.stderr}"}

            # 解析服务列表
            services = []
            lines = result.stdout.split('\n')

            # 跳过标题行
            for line in lines[1:]:
                line = line.strip()
                if not line or line.startswith("●") or line.startswith("○"):
                    continue

                # 分割行
                parts = line.split()
                if len(parts) < 4:
                    continue

                name = parts[0].replace(".service", "")
                loaded = parts[1]
                active = parts[2]
                sub = parts[3]

                service = {
                    "name": name,
                    "loaded": loaded,
                    "active": active,
                    "sub": sub
                }

                # 如果需要详细信息
                if detailed:
                    detailed_info = self._get_unix_service_info(name)
                    if detailed_info.get("success"):
                        service.update(detailed_info.get("service", {}))

                services.append(service)

            logger.info(f"列出Unix服务: 找到 {len(services)} 个服务")

            return {
                "success": True,
                "services": services,
                "count": len(services),
                "system": self.system
            }
        except Exception as e:
            error_msg = f"列出Unix服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_service_info(self, name: str) -> Dict[str, Any]:
        """
        获取服务信息

        参数:
            name: 服务名称

        返回:
            服务信息
        """
        try:
            if self.system == 'windows':
                return self._get_windows_service_info(name)
            elif self.system in ['linux', 'darwin']:
                return self._get_unix_service_info(name)
            else:
                return {"error": f"不支持的系统: {self.system}"}
        except Exception as e:
            error_msg = f"获取服务信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _get_windows_service_info(self, name: str) -> Dict[str, Any]:
        """
        获取Windows系统服务信息

        参数:
            name: 服务名称

        返回:
            服务信息
        """
        try:
            # 使用sc queryex命令获取详细信息
            result = subprocess.run(
                ["sc", "queryex", "name=" + name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {"error": f"获取服务信息失败: {result.stderr}"}

            # 解析服务信息
            service = {}
            for line in result.stdout.split('\n'):
                if not line:
                    continue

                if line.startswith("SERVICE_NAME:"):
                    service["name"] = line.split(":", 1)[1].strip()
                elif line.startswith("STATE:"):
                    service["state"] = line.split(":", 1)[1].strip()
                elif line.startswith("TYPE:"):
                    service["type"] = line.split(":", 1)[1].strip()
                elif line.startswith("WIN32_EXIT_CODE:"):
                    service["win32_exit_code"] = line.split(":", 1)[1].strip()
                elif line.startswith("SERVICE_EXIT_CODE:"):
                    service["service_exit_code"] = line.split(":", 1)[1].strip()
                elif line.startswith("CHECKPOINT:"):
                    service["checkpoint"] = line.split(":", 1)[1].strip()
                elif line.startswith("WAIT_HINT:"):
                    service["wait_hint"] = line.split(":", 1)[1].strip()
                elif line.startswith("PID:"):
                    service["process_id"] = line.split(":", 1)[1].strip()

            # 获取服务配置
            config_result = subprocess.run(
                ["sc", "qc", name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if config_result.returncode == 0:
                service["config"] = {}
                for line in config_result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue

                    if line.startswith("BINARY_PATH_NAME:"):
                        service["config"]["binary_path"] = line.split(":", 1)[1].strip()
                    elif line.startswith("START_TYPE:"):
                        service["config"]["start_type"] = line.split(":", 1)[1].strip()
                    elif line.startswith("ERROR_CONTROL:"):
                        service["config"]["error_control"] = line.split(":", 1)[1].strip()
                    elif line.startswith("DEPENDENCIES:"):
                        service["config"]["dependencies"] = line.split(":", 1)[1].strip()
                    elif line.startswith("SERVICE_START_NAME:"):
                        service["config"]["start_name"] = line.split(":", 1)[1].strip()

            logger.info(f"获取Windows服务信息: {name}")

            return {
                "success": True,
                "service": service
            }
        except Exception as e:
            error_msg = f"获取Windows服务信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _get_unix_service_info(self, name: str) -> Dict[str, Any]:
        """
        获取Unix系统服务信息

        参数:
            name: 服务名称

        返回:
            服务信息
        """
        try:
            # 使用systemctl show命令获取详细信息
            result = subprocess.run(
                ["systemctl", "show", name + ".service"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {"error": f"获取服务信息失败: {result.stderr}"}

            # 解析服务信息
            service = {}
            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if "=" in line:
                    key, value = line.split("=", 1)
                    service[key.lower()] = value.strip()

            # 获取服务状态
            status_result = subprocess.run(
                ["systemctl", "status", name + ".service"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if status_result.returncode == 0:
                service["status_output"] = status_result.stdout

            logger.info(f"获取Unix服务信息: {name}")

            return {
                "success": True,
                "service": service
            }
        except Exception as e:
            error_msg = f"获取Unix服务信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def start_service(self, name: str) -> Dict[str, Any]:
        """
        启动服务

        参数:
            name: 服务名称

        返回:
            操作结果
        """
        try:
            if self.system == 'windows':
                result = subprocess.run(
                    ["sc", "start", name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"启动Windows服务: {name}")
                    return {
                        "success": True,
                        "message": f"已启动服务: {name}"
                    }
                else:
                    return {
                        "error": f"启动服务失败: {result.stderr}"
                    }

            elif self.system in ['linux', 'darwin']:
                result = subprocess.run(
                    ["systemctl", "start", name + ".service"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"启动Unix服务: {name}")
                    return {
                        "success": True,
                        "message": f"已启动服务: {name}"
                    }
                else:
                    return {
                        "error": f"启动服务失败: {result.stderr}"
                    }

            else:
                return {"error": f"不支持的系统: {self.system}"}
        except Exception as e:
            error_msg = f"启动服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def stop_service(self, name: str) -> Dict[str, Any]:
        """
        停止服务

        参数:
            name: 服务名称

        返回:
            操作结果
        """
        try:
            if self.system == 'windows':
                result = subprocess.run(
                    ["sc", "stop", name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"停止Windows服务: {name}")
                    return {
                        "success": True,
                        "message": f"已停止服务: {name}"
                    }
                else:
                    return {
                        "error": f"停止服务失败: {result.stderr}"
                    }

            elif self.system in ['linux', 'darwin']:
                result = subprocess.run(
                    ["systemctl", "stop", name + ".service"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"停止Unix服务: {name}")
                    return {
                        "success": True,
                        "message": f"已停止服务: {name}"
                    }
                else:
                    return {
                        "error": f"停止服务失败: {result.stderr}"
                    }

            else:
                return {"error": f"不支持的系统: {self.system}"}
        except Exception as e:
            error_msg = f"停止服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def restart_service(self, name: str) -> Dict[str, Any]:
        """
        重启服务

        参数:
            name: 服务名称

        返回:
            操作结果
        """
        try:
            if self.system == 'windows':
                result = subprocess.run(
                    ["sc", "stop", name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode != 0:
                    return {
                        "error": f"停止服务失败: {result.stderr}"
                    }

                result = subprocess.run(
                    ["sc", "start", name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"重启Windows服务: {name}")
                    return {
                        "success": True,
                        "message": f"已重启服务: {name}"
                    }
                else:
                    return {
                        "error": f"启动服务失败: {result.stderr}"
                    }

            elif self.system in ['linux', 'darwin']:
                result = subprocess.run(
                    ["systemctl", "restart", name + ".service"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"重启Unix服务: {name}")
                    return {
                        "success": True,
                        "message": f"已重启服务: {name}"
                    }
                else:
                    return {
                        "error": f"重启服务失败: {result.stderr}"
                    }

            else:
                return {"error": f"不支持的系统: {self.system}"}
        except Exception as e:
            error_msg = f"重启服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def enable_service(self, name: str) -> Dict[str, Any]:
        """
        启用服务

        参数:
            name: 服务名称

        返回:
            操作结果
        """
        try:
            if self.system == 'windows':
                result = subprocess.run(
                    ["sc", "config", name, "start=", "auto"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"启用Windows服务: {name}")
                    return {
                        "success": True,
                        "message": f"已启用服务: {name}"
                    }
                else:
                    return {
                        "error": f"启用服务失败: {result.stderr}"
                    }

            elif self.system in ['linux', 'darwin']:
                result = subprocess.run(
                    ["systemctl", "enable", name + ".service"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"启用Unix服务: {name}")
                    return {
                        "success": True,
                        "message": f"已启用服务: {name}"
                    }
                else:
                    return {
                        "error": f"启用服务失败: {result.stderr}"
                    }

            else:
                return {"error": f"不支持的系统: {self.system}"}
        except Exception as e:
            error_msg = f"启用服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def disable_service(self, name: str) -> Dict[str, Any]:
        """
        禁用服务

        参数:
            name: 服务名称

        返回:
            操作结果
        """
        try:
            if self.system == 'windows':
                result = subprocess.run(
                    ["sc", "config", name, "start=", "demand"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"禁用Windows服务: {name}")
                    return {
                        "success": True,
                        "message": f"已禁用服务: {name}"
                    }
                else:
                    return {
                        "error": f"禁用服务失败: {result.stderr}"
                    }

            elif self.system in ['linux', 'darwin']:
                result = subprocess.run(
                    ["systemctl", "disable", name + ".service"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    logger.info(f"禁用Unix服务: {name}")
                    return {
                        "success": True,
                        "message": f"已禁用服务: {name}"
                    }
                else:
                    return {
                        "error": f"禁用服务失败: {result.stderr}"
                    }

            else:
                return {"error": f"不支持的系统: {self.system}"}
        except Exception as e:
            error_msg = f"禁用服务失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
