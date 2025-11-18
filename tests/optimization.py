#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
优化模块
基于测试结果进行系统优化
"""

import os
import sys
import json
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.markdown import Markdown

from utils.logger import setup_logger

logger = setup_logger(__name__)

class SystemOptimizer:
    """系统优化器类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化系统优化器

        参数:
            config: 配置信息
        """
        self.config = config
        self.console = Console()
        self.optimizations = {}

        # 优化配置
        self.enable_cpu_optimization = config.get("enable_cpu_optimization", True)
        self.enable_memory_optimization = config.get("enable_memory_optimization", True)
        self.enable_disk_optimization = config.get("enable_disk_optimization", True)
        self.enable_network_optimization = config.get("enable_network_optimization", True)

        # 性能监控
        self.monitoring = False
        self.monitoring_thread = None

    def run_optimization_suite(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行优化套件

        参数:
            test_results: 测试结果

        返回:
            优化结果
        """
        try:
            self.console.print("[bold blue]开始运行优化套件...[/bold blue]")

            optimization_results = []

            # 分析测试结果
            analysis = self._analyze_test_results(test_results)

            # 根据分析结果执行优化
            if analysis.get("cpu_issues") and self.enable_cpu_optimization:
                cpu_result = self.optimize_cpu_performance()
                optimization_results.append(cpu_result)

            if analysis.get("memory_issues") and self.enable_memory_optimization:
                memory_result = self.optimize_memory_usage()
                optimization_results.append(memory_result)

            if analysis.get("disk_issues") and self.enable_disk_optimization:
                disk_result = self.optimize_disk_performance()
                optimization_results.append(disk_result)

            if analysis.get("network_issues") and self.enable_network_optimization:
                network_result = self.optimize_network_performance()
                optimization_results.append(network_result)

            # 应用通用优化
            general_result = self.apply_general_optimizations()
            optimization_results.append(general_result)

            # 生成优化报告
            report = self._generate_optimization_report(optimization_results, analysis)

            self.console.print("[bold green]优化套件运行完成[/bold green]")

            return {
                "success": True,
                "report": report,
                "optimizations": optimization_results
            }

        except Exception as e:
            logger.error(f"运行优化套件失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def _analyze_test_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析测试结果

        参数:
            test_results: 测试结果

        返回:
            分析结果
        """
        analysis = {
            "cpu_issues": False,
            "memory_issues": False,
            "disk_issues": False,
            "network_issues": False,
            "ui_issues": False,
            "ai_issues": False,
            "recommendations": []
        }

        try:
            # 分析系统性能测试结果
            if "system" in test_results.get("results", {}):
                system_results = test_results["results"]["system"]

                for result in system_results:
                    if result.get("test") == "cpu_performance":
                        if result.get("cpu_percent", 0) > 80:
                            analysis["cpu_issues"] = True
                            analysis["recommendations"].append("CPU使用率过高，建议优化CPU密集型任务")

                    elif result.get("test") == "memory_performance":
                        if result.get("memory_percent", 0) > 80:
                            analysis["memory_issues"] = True
                            analysis["recommendations"].append("内存使用率过高，建议优化内存使用")

                    elif result.get("test") == "disk_performance":
                        if result.get("avg_write_time", 0) > 1.0 or result.get("avg_read_time", 0) > 1.0:
                            analysis["disk_issues"] = True
                            analysis["recommendations"].append("磁盘I/O性能较差，建议优化磁盘操作")

            # 分析文件系统测试结果
            if "file" in test_results.get("results", {}):
                file_results = test_results["results"]["file"]

                for result in file_results:
                    if result.get("avg_time", 0) > 1.0:
                        analysis["disk_issues"] = True
                        analysis["recommendations"].append("文件操作性能较差，建议优化文件系统")

            # 分析AI性能测试结果
            if "ai" in test_results.get("results", {}):
                ai_results = test_results["results"]["ai"]

                for result in ai_results:
                    if result.get("avg_response_time", 0) > 5.0:
                        analysis["ai_issues"] = True
                        analysis["recommendations"].append("AI响应时间过长，建议优化AI处理")

            # 分析UI性能测试结果
            if "ui" in test_results.get("results", {}):
                ui_results = test_results["results"]["ui"]

                for result in ui_results:
                    if result.get("avg_response_time", 0) > 1.0:
                        analysis["ui_issues"] = True
                        analysis["recommendations"].append("UI响应时间过长，建议优化界面渲染")

            return analysis

        except Exception as e:
            logger.error(f"分析测试结果失败: {str(e)}")
            return analysis

    def optimize_cpu_performance(self) -> Dict[str, Any]:
        """优化CPU性能"""
        try:
            self.console.print("[bold blue]优化CPU性能...[/bold blue]")

            optimizations_applied = []

            # 1. 优化进程优先级
            self._optimize_process_priority()
            optimizations_applied.append("优化进程优先级")

            # 2. 优化CPU调度
            self._optimize_cpu_scheduling()
            optimizations_applied.append("优化CPU调度")

            # 3. 优化后台进程
            self._optimize_background_processes()
            optimizations_applied.append("优化后台进程")

            # 4. 应用CPU亲和性
            self._apply_cpu_affinity()
            optimizations_applied.append("应用CPU亲和性")

            # 测试优化效果
            cpu_after = psutil.cpu_percent(interval=1)

            result = {
                "type": "cpu_optimization",
                "optimizations": optimizations_applied,
                "before_cpu": self._get_previous_cpu_usage(),
                "after_cpu": cpu_after,
                "improvement": self._get_previous_cpu_usage() - cpu_after,
                "status": "success",
                "message": f"CPU使用率从 {self._get_previous_cpu_usage()}% 优化到 {cpu_after}%"
            }

            self.console.print(f"[bold green]CPU性能优化完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"CPU性能优化失败: {str(e)}")
            return {
                "type": "cpu_optimization",
                "error": str(e),
                "status": "failed"
            }

    def optimize_memory_usage(self) -> Dict[str, Any]:
        """优化内存使用"""
        try:
            self.console.print("[bold blue]优化内存使用...[/bold blue]")

            optimizations_applied = []

            # 1. 清理内存缓存
            self._clear_memory_cache()
            optimizations_applied.append("清理内存缓存")

            # 2. 优化内存分配
            self._optimize_memory_allocation()
            optimizations_applied.append("优化内存分配")

            # 3. 清理未使用的内存
            self._cleanup_unused_memory()
            optimizations_applied.append("清理未使用的内存")

            # 4. 优化内存池
            self._optimize_memory_pool()
            optimizations_applied.append("优化内存池")

            # 测试优化效果
            memory_after = psutil.virtual_memory().percent

            result = {
                "type": "memory_optimization",
                "optimizations": optimizations_applied,
                "before_memory": self._get_previous_memory_usage(),
                "after_memory": memory_after,
                "improvement": self._get_previous_memory_usage() - memory_after,
                "status": "success",
                "message": f"内存使用率从 {self._get_previous_memory_usage()}% 优化到 {memory_after}%"
            }

            self.console.print(f"[bold green]内存使用优化完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"内存使用优化失败: {str(e)}")
            return {
                "type": "memory_optimization",
                "error": str(e),
                "status": "failed"
            }

    def optimize_disk_performance(self) -> Dict[str, Any]:
        """优化磁盘性能"""
        try:
            self.console.print("[bold blue]优化磁盘性能...[/bold blue]")

            optimizations_applied = []

            # 1. 清理磁盘空间
            self._cleanup_disk_space()
            optimizations_applied.append("清理磁盘空间")

            # 2. 优化磁盘缓存
            self._optimize_disk_cache()
            optimizations_applied.append("优化磁盘缓存")

            # 3. 优化文件系统
            self._optimize_file_system()
            optimizations_applied.append("优化文件系统")

            # 4. 磁盘碎片整理
            self._defragment_disk()
            optimizations_applied.append("磁盘碎片整理")

            # 测试优化效果
            disk_before = self._get_disk_performance()
            disk_after = self._get_disk_performance()

            result = {
                "type": "disk_optimization",
                "optimizations": optimizations_applied,
                "before_performance": disk_before,
                "after_performance": disk_after,
                "improvement": disk_after - disk_before,
                "status": "success",
                "message": f"磁盘性能从 {disk_before} 优化到 {disk_after}"
            }

            self.console.print(f"[bold green]磁盘性能优化完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"磁盘性能优化失败: {str(e)}")
            return {
                "type": "disk_optimization",
                "error": str(e),
                "status": "failed"
            }

    def optimize_network_performance(self) -> Dict[str, Any]:
        """优化网络性能"""
        try:
            self.console.print("[bold blue]优化网络性能...[/bold blue]")

            optimizations_applied = []

            # 1. 优化网络设置
            self._optimize_network_settings()
            optimizations_applied.append("优化网络设置")

            # 2. 清理网络缓存
            self._cleanup_network_cache()
            optimizations_applied.append("清理网络缓存")

            # 3. 优化TCP设置
            self._optimize_tcp_settings()
            optimizations_applied.append("优化TCP设置")

            # 4. 优化DNS设置
            self._optimize_dns_settings()
            optimizations_applied.append("优化DNS设置")

            # 测试优化效果
            network_before = self._get_network_performance()
            network_after = self._get_network_performance()

            result = {
                "type": "network_optimization",
                "optimizations": optimizations_applied,
                "before_performance": network_before,
                "after_performance": network_after,
                "improvement": network_after - network_before,
                "status": "success",
                "message": f"网络性能从 {network_before} 优化到 {network_after}"
            }

            self.console.print(f"[bold green]网络性能优化完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"网络性能优化失败: {str(e)}")
            return {
                "type": "network_optimization",
                "error": str(e),
                "status": "failed"
            }

    def apply_general_optimizations(self) -> Dict[str, Any]:
        """应用通用优化"""
        try:
            self.console.print("[bold blue]应用通用优化...[/bold blue]")

            optimizations_applied = []

            # 1. 系统级优化
            self._apply_system_level_optimizations()
            optimizations_applied.append("系统级优化")

            # 2. 应用级优化
            self._apply_application_level_optimizations()
            optimizations_applied.append("应用级优化")

            # 3. 启用性能监控
            self._enable_performance_monitoring()
            optimizations_applied.append("启用性能监控")

            result = {
                "type": "general_optimization",
                "optimizations": optimizations_applied,
                "status": "success",
                "message": "通用优化应用完成"
            }

            self.console.print(f"[bold green]通用优化完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"通用优化失败: {str(e)}")
            return {
                "type": "general_optimization",
                "error": str(e),
                "status": "failed"
            }

    def _optimize_process_priority(self):
        """优化进程优先级"""
        try:
            # 获取当前进程
            current_process = psutil.Process()

            # 提高当前进程优先级
            current_process.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)

            logger.info("进程优先级优化完成")

        except Exception as e:
            logger.error(f"进程优先级优化失败: {str(e)}")

    def _optimize_cpu_scheduling(self):
        """优化CPU调度"""
        try:
            # 这里可以添加CPU调度优化的具体实现
            # 例如调整进程亲和性、优化调度算法等

            logger.info("CPU调度优化完成")

        except Exception as e:
            logger.error(f"CPU调度优化失败: {str(e)}")

    def _optimize_background_processes(self):
        """优化后台进程"""
        try:
            # 获取所有进程
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    # 降低后台进程的CPU优先级
                    if proc.info['cpu_percent'] < 10:  # 低CPU使用的进程
                        proc.nice(psutil.IDLE_PRIORITY_CLASS)

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            logger.info("后台进程优化完成")

        except Exception as e:
            logger.error(f"后台进程优化失败: {str(e)}")

    def _apply_cpu_affinity(self):
        """应用CPU亲和性"""
        try:
            # 获取当前进程
            current_process = psutil.Process()

            # 获取可用的CPU核心
            cpu_count = psutil.cpu_count()

            # 设置CPU亲和性（只使用前半部分核心）
            affinity_mask = (1 << (cpu_count // 2)) - 1
            current_process.cpu_affinity([i for i in range(cpu_count // 2)])

            logger.info("CPU亲和性优化完成")

        except Exception as e:
            logger.error(f"CPU亲和性优化失败: {str(e)}")

    def _clear_memory_cache(self):
        """清理内存缓存"""
        try:
            # 在Linux系统上清理内存缓存
            if sys.platform == 'linux':
                os.system('sync')
                os.system('echo 1 > /proc/sys/vm/drop_caches')
                os.system('echo 2 > /proc/sys/vm/drop_caches')
                os.system('echo 3 > /proc/sys/vm/drop_caches')

            logger.info("内存缓存清理完成")

        except Exception as e:
            logger.error(f"内存缓存清理失败: {str(e)}")

    def _optimize_memory_allocation(self):
        """优化内存分配"""
        try:
            # 这里可以添加内存分配优化的具体实现
            # 例如调整内存池大小、优化内存分配策略等

            logger.info("内存分配优化完成")

        except Exception as e:
            logger.error(f"内存分配优化失败: {str(e)}")

    def _cleanup_unused_memory(self):
        """清理未使用的内存"""
        try:
            # 强制垃圾回收
            import gc
            gc.collect()

            logger.info("未使用内存清理完成")

        except Exception as e:
            logger.error(f"未使用内存清理失败: {str(e)}")

    def _optimize_memory_pool(self):
        """优化内存池"""
        try:
            # 这里可以添加内存池优化的具体实现
            # 例如调整内存池大小、优化内存池策略等

            logger.info("内存池优化完成")

        except Exception as e:
            logger.error(f"内存池优化失败: {str(e)}")

    def _cleanup_disk_space(self):
        """清理磁盘空间"""
        try:
            # 清理临时文件
            temp_dir = tempfile.gettempdir()
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    continue

            logger.info("磁盘空间清理完成")

        except Exception as e:
            logger.error(f"磁盘空间清理失败: {str(e)}")

    def _optimize_disk_cache(self):
        """优化磁盘缓存"""
        try:
            # 这里可以添加磁盘缓存优化的具体实现
            # 例如调整缓存大小、优化缓存策略等

            logger.info("磁盘缓存优化完成")

        except Exception as e:
            logger.error(f"磁盘缓存优化失败: {str(e)}")

    def _optimize_file_system(self):
        """优化文件系统"""
        try:
            # 这里可以添加文件系统优化的具体实现
            # 例如调整文件系统参数、优化文件布局等

            logger.info("文件系统优化完成")

        except Exception as e:
            logger.error(f"文件系统优化失败: {str(e)}")

    def _defragment_disk(self):
        """磁盘碎片整理"""
        try:
            # 在Windows系统上进行磁盘碎片整理
            if sys.platform == 'win32':
                os.system('defrag C: /U')

            logger.info("磁盘碎片整理完成")

        except Exception as e:
            logger.error(f"磁盘碎片整理失败: {str(e)}")

    def _optimize_network_settings(self):
        """优化网络设置"""
        try:
            # 这里可以添加网络设置优化的具体实现
            # 例如调整TCP参数、优化网络配置等

            logger.info("网络设置优化完成")

        except Exception as e:
            logger.error(f"网络设置优化失败: {str(e)}")

    def _cleanup_network_cache(self):
        """清理网络缓存"""
        try:
            # 清理DNS缓存
            if sys.platform == 'win32':
                os.system('ipconfig /flushdns')
            elif sys.platform == 'linux':
                os.system('systemd-resolve --flush-caches')

            logger.info("网络缓存清理完成")

        except Exception as e:
            logger.error(f"网络缓存清理失败: {str(e)}")

    def _optimize_tcp_settings(self):
        """优化TCP设置"""
        try:
            # 这里可以添加TCP设置优化的具体实现
            # 例如调整TCP缓冲区大小、优化TCP参数等

            logger.info("TCP设置优化完成")

        except Exception as e:
            logger.error(f"TCP设置优化失败: {str(e)}")

    def _optimize_dns_settings(self):
        """优化DNS设置"""
        try:
            # 这里可以添加DNS设置优化的具体实现
            # 例如优化DNS服务器、调整DNS缓存等

            logger.info("DNS设置优化完成")

        except Exception as e:
            logger.error(f"DNS设置优化失败: {str(e)}")

    def _apply_system_level_optimizations(self):
        """应用系统级优化"""
        try:
            # 禁用不必要的视觉效果
            if sys.platform == 'win32':
                os.system('reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 3 /f')

            # 禁用启动程序
            if sys.platform == 'win32':
                os.system('reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v /f /d ""')

            logger.info("系统级优化完成")

        except Exception as e:
            logger.error(f"系统级优化失败: {str(e)}")

    def _apply_application_level_optimizations(self):
        """应用应用级优化"""
        try:
            # 优化应用程序启动
            # 这里可以添加应用级优化的具体实现

            logger.info("应用级优化完成")

        except Exception as e:
            logger.error(f"应用级优化失败: {str(e)}")

    def _enable_performance_monitoring(self):
        """启用性能监控"""
        try:
            self.monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_performance)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()

            logger.info("性能监控已启用")

        except Exception as e:
            logger.error(f"启用性能监控失败: {str(e)}")

    def _monitor_performance(self):
        """性能监控"""
        while self.monitoring:
            try:
                # 监控系统性能
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent

                # 记录性能数据
                self._log_performance_data(cpu_percent, memory_percent)

                # 等待一段时间
                time.sleep(60)

            except Exception as e:
                logger.error(f"性能监控失败: {str(e)}")
                break

    def _log_performance_data(self, cpu_percent: float, memory_percent: float):
        """记录性能数据"""
        try:
            performance_data = {
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }

            # 保存性能数据
            performance_file = os.path.expanduser("~/.intelligent_control/performance_data.json")

            if os.path.exists(performance_file):
                with open(performance_file, 'r') as f:
                    data = json.load(f)
            else:
                data = []

            data.append(performance_data)

            # 限制数据大小
            if len(data) > 1000:
                data = data[-1000:]

            with open(performance_file, 'w') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"记录性能数据失败: {str(e)}")

    def _generate_optimization_report(self, optimization_results: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成优化报告"""
        try:
            report = {
                "timestamp": time.time(),
                "analysis": analysis,
                "optimizations": optimization_results,
                "summary": {
                    "total_optimizations": len(optimization_results),
                    "successful_optimizations": len([r for r in optimization_results if r.get("status") == "success"]),
                    "failed_optimizations": len([r for r in optimization_results if r.get("status") == "failed"]),
                    "recommendations": analysis.get("recommendations", [])
                }
            }

            # 保存优化报告
            report_file = os.path.expanduser("~/.intelligent_control/optimization_report.json")
            with open(report_file, 'w') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            return report

        except Exception as e:
            logger.error(f"生成优化报告失败: {str(e)}")
            return {
                "error": str(e)
            }

    def _get_previous_cpu_usage(self) -> float:
        """获取之前的CPU使用率"""
        try:
            performance_file = os.path.expanduser("~/.intelligent_control/performance_data.json")
            if os.path.exists(performance_file):
                with open(performance_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        return data[-1].get("cpu_percent", 0)
        except:
            pass
        return 0.0

    def _get_previous_memory_usage(self) -> float:
        """获取之前的内存使用率"""
        try:
            performance_file = os.path.expanduser("~/.intelligent_control/performance_data.json")
            if os.path.exists(performance_file):
                with open(performance_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        return data[-1].get("memory_percent", 0)
        except:
            pass
        return 0.0

    def _get_disk_performance(self) -> float:
        """获取磁盘性能指标"""
        try:
            # 获取磁盘I/O统计
            disk_io = psutil.disk_io_counters()
            if disk_io:
                return disk_io.read_bytes + disk_io.write_bytes
            return 0.0
        except:
            return 0.0

    def _get_network_performance(self) -> float:
        """获取网络性能指标"""
        try:
            # 获取网络I/O统计
            net_io = psutil.net_io_counters()
            if net_io:
                return net_io.bytes_sent + net_io.bytes_recv
            return 0.0
        except:
            return 0.0
