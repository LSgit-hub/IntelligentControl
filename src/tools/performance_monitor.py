#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统性能监控工具模块
提供系统性能监控功能
"""

import os
import sys
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PerformanceMonitor:
    """性能监控器类"""

    def __init__(self):
        """初始化性能监控器"""
        # self.system = psutil.system_cpu_times()
        self.monitoring = False
        self.monitor_thread = None
        self.monitor_data = []
        self.max_data_points = 100
        self.callbacks = {}

        # 性能计数器
        self.cpu_times = psutil.cpu_times()
        self.cpu_percent = psutil.cpu_percent(interval=0)
        self.memory_info = psutil.virtual_memory()
        self.swap_info = psutil.swap_memory()
        self.disk_io = psutil.disk_io_counters()
        self.network_io = psutil.net_io_counters()

    def start_monitoring(self, interval: float = 1.0) -> Dict[str, Any]:
        """
        开始性能监控

        参数:
            interval: 监控间隔（秒）

        返回:
            操作结果
        """
        if self.monitoring:
            return {"error": "监控已经在运行"}

        try:
            self.monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(interval,),
                daemon=True
            )
            self.monitor_thread.start()

            logger.info(f"开始性能监控，间隔: {interval}秒")
            return {
                "success": True,
                "message": f"已开始性能监控，间隔: {interval}秒"
            }
        except Exception as e:
            error_msg = f"启动性能监控失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def stop_monitoring(self) -> Dict[str, Any]:
        """
        停止性能监控

        返回:
            操作结果
        """
        if not self.monitoring:
            return {"error": "监控未运行"}

        try:
            self.monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)

            logger.info("停止性能监控")
            return {
                "success": True,
                "message": "已停止性能监控"
            }
        except Exception as e:
            error_msg = f"停止性能监控失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_current_stats(self) -> Dict[str, Any]:
        """
        获取当前性能统计信息

        返回:
            当前性能统计信息
        """
        try:
            stats = {
                "timestamp": time.time(),
                "cpu": {
                    "percent": psutil.cpu_percent(interval=0.1),
                    "count": psutil.cpu_count(),
                    "logical_count": psutil.cpu_count(logical=True),
                    "times": psutil.cpu_times()._asdict(),
                    "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None
                },
                "memory": {
                    "total": self.memory_info.total,
                    "available": self.memory_info.available,
                    "percent": self.memory_info.percent,
                    "used": self.memory_info.used,
                    "free": self.memory_info.free,
                    "cached": getattr(self.memory_info, "cached", 0),
                    "buffers": getattr(self.memory_info, "buffers", 0)
                },
                "swap": {
                    "total": self.swap_info.total,
                    "used": self.swap_info.used,
                    "percent": self.swap_info.percent,
                    "free": self.swap_info.total - self.swap_info.used
                },
                "disk": {
                    "io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
                    "partitions": []
                },
                "network": {
                    "io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None,
                    "interfaces": {}
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
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                    stats["disk"]["partitions"].append(partition_info)
                except Exception:
                    continue

            # 获取网络接口信息
            for interface, addrs in psutil.net_if_addrs().items():
                stats["network"]["interfaces"][interface] = []
                for addr in addrs:
                    addr_info = {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    }
                    stats["network"]["interfaces"][interface].append(addr_info)

            logger.info("获取当前性能统计信息成功")
            return {
                "success": True,
                "stats": stats
            }
        except Exception as e:
            error_msg = f"获取当前性能统计信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_monitoring_data(self, count: int = 10) -> Dict[str, Any]:
        """
        获取监控数据

        参数:
            count: 返回的数据点数量

        返回:
            监控数据
        """
        try:
            if not self.monitor_data:
                return {"error": "没有监控数据"}

            # 获取指定数量的数据点
            data_points = self.monitor_data[-count:]

            logger.info(f"获取监控数据成功，数据点数: {len(data_points)}")
            return {
                "success": True,
                "data": data_points,
                "count": len(data_points)
            }
        except Exception as e:
            error_msg = f"获取监控数据失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def add_callback(self, event: str, callback: Callable) -> Dict[str, Any]:
        """
        添加监控回调函数

        参数:
            event: 事件名称
            callback: 回调函数

        返回:
            操作结果
        """
        if event not in self.callbacks:
            self.callbacks[event] = []

        self.callbacks[event].append(callback)

        logger.info(f"添加监控回调函数: {event}")
        return {
            "success": True,
            "message": f"已添加回调函数: {event}"
        }

    def remove_callback(self, event: str, callback: Callable) -> Dict[str, Any]:
        """
        移除监控回调函数

        参数:
            event: 事件名称
            callback: 回调函数

        返回:
            操作结果
        """
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)

            logger.info(f"移除监控回调函数: {event}")
            return {
                "success": True,
                "message": f"已移除回调函数: {event}"
            }

        return {"error": f"找不到回调函数: {event}"}

    def _monitor_loop(self, interval: float) -> None:
        """
        监控循环

        参数:
            interval: 监控间隔（秒）
        """
        while self.monitoring:
            try:
                # 收集性能数据
                data = self._collect_performance_data()

                # 添加到监控数据
                self.monitor_data.append(data)

                # 限制数据点数量
                if len(self.monitor_data) > self.max_data_points:
                    self.monitor_data.pop(0)

                # 调用回调函数
                self._call_callbacks(data)

                # 等待
                time.sleep(interval)
            except Exception as e:
                logger.error(f"性能监控错误: {str(e)}")
                time.sleep(interval)

    def _collect_performance_data(self) -> Dict[str, Any]:
        """
        收集性能数据

        返回:
            性能数据
        """
        data = {
            "timestamp": time.time(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=0),
                "times": psutil.cpu_times()._asdict()
            },
            "memory": {
                "total": self.memory_info.total,
                "available": self.memory_info.available,
                "percent": self.memory_info.percent,
                "used": self.memory_info.used,
                "free": self.memory_info.free
            },
            "swap": {
                "total": self.swap_info.total,
                "used": self.swap_info.used,
                "percent": self.swap_info.percent,
                "free": self.swap_info.total - self.swap_info.used
            },
            "disk": {
                "io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None
            },
            "network": {
                "io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
            }
        }

        return data

    def _call_callbacks(self, data: Dict[str, Any]) -> None:
        """
        调用回调函数

        参数:
            data: 性能数据
        """
        for event, callbacks in self.callbacks.items():
            for callback in callbacks:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"回调函数执行错误: {str(e)}")

    def get_process_stats(self, pid: int) -> Dict[str, Any]:
        """
        获取指定进程的性能统计信息

        参数:
            pid: 进程ID

        返回:
            进程性能统计信息
        """
        try:
            proc = psutil.Process(pid)

            stats = {
                "pid": pid,
                "name": proc.name(),
                "status": proc.status(),
                "cpu_percent": proc.cpu_percent(interval=0.1),
                "memory_percent": proc.memory_percent(),
                "memory_info": proc.memory_info()._asdict() if proc.memory_info() else None,
                "io_counters": proc.io_counters()._asdict() if proc.io_counters() else None,
                "num_threads": proc.num_threads(),
                "threads": proc.threads(),
                "cpu_times": proc.cpu_times()._asdict() if proc.cpu_times() else None,
                "create_time": proc.create_time()
            }

            logger.info(f"获取进程性能统计信息成功: {pid}")
            return {
                "success": True,
                "stats": stats
            }
        except psutil.NoSuchProcess:
            error_msg = f"进程不存在: {pid}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"获取进程性能统计信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_top_processes(self, limit: int = 10, by: str = "cpu") -> Dict[str, Any]:
        """
        获取资源使用率最高的进程

        参数:
            limit: 返回的进程数量
            by: 排序字段（cpu, memory, io）

        返回:
            进程列表
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'io_counters']):
                try:
                    proc_info = proc.info
                    processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 排序
            if by == "cpu":
                processes.sort(key=lambda p: p.get('cpu_percent', 0), reverse=True)
            elif by == "memory":
                processes.sort(key=lambda p: p.get('memory_percent', 0), reverse=True)
            elif by == "io":
                processes.sort(key=lambda p: p.get('io_counters', {}).get('read_bytes', 0) + 
                              p.get('io_counters', {}).get('write_bytes', 0), reverse=True)
            else:
                processes.sort(key=lambda p: p.get('cpu_percent', 0), reverse=True)

            # 限制数量
            top_processes = processes[:limit]

            logger.info(f"获取Top {limit}进程成功")
            return {
                "success": True,
                "processes": top_processes,
                "count": len(top_processes),
                "sorted_by": by
            }
        except Exception as e:
            error_msg = f"获取Top进程失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
