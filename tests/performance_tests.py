#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
性能测试模块
测试系统性能和响应时间
"""

import os
import sys
import time
import threading
import psutil
import statistics
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.markdown import Markdown

from utils.logger import setup_logger

logger = setup_logger(__name__)

class PerformanceTests:
    """性能测试类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化性能测试

        参数:
            config: 配置信息
        """
        self.config = config
        self.console = Console()
        self.results = []

        # 测试配置
        self.test_iterations = config.get("test_iterations", 100)
        self.test_concurrency = config.get("test_concurrency", 10)
        self.timeout = config.get("timeout", 30)

        # 性能基准
        self.baseline_metrics = {
            "cpu_threshold": 80,  # CPU使用率阈值(%)
            "memory_threshold": 80,  # 内存使用率阈值(%)
            "response_time_threshold": 5.0,  # 响应时间阈值(秒)
            "throughput_threshold": 100  # 吞吐量阈值(请求/秒)
        }

    def run_performance_suite(self, suite_name: str) -> Dict[str, Any]:
        """
        运行性能测试套件

        参数:
            suite_name: 测试套件名称

        返回:
            测试结果
        """
        try:
            self.console.print(f"[bold blue]开始运行性能测试套件: {suite_name}[/bold blue]")

            # 根据套件选择测试
            if suite_name == "system":
                return self.run_system_performance_tests()
            elif suite_name == "file":
                return self.run_file_performance_tests()
            elif suite_name == "ai":
                return self.run_ai_performance_tests()
            elif suite_name == "ui":
                return self.run_ui_performance_tests()
            elif suite_name == "all":
                return self.run_all_performance_tests()
            else:
                return {
                    "success": False,
                    "error": f"未知的性能测试套件: {suite_name}"
                }

        except Exception as e:
            logger.error(f"运行性能测试套件失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def run_system_performance_tests(self) -> Dict[str, Any]:
        """运行系统性能测试"""
        results = []

        # CPU性能测试
        cpu_result = self.test_cpu_performance()
        results.append(cpu_result)

        # 内存性能测试
        memory_result = self.test_memory_performance()
        results.append(memory_result)

        # 磁盘I/O性能测试
        disk_result = self.test_disk_performance()
        results.append(disk_result)

        # 网络性能测试
        network_result = self.test_network_performance()
        results.append(network_result)

        # 进程创建性能测试
        process_result = self.test_process_creation()
        results.append(process_result)

        return {
            "success": True,
            "suite": "system",
            "results": results,
            "summary": self._generate_performance_summary(results)
        }

    def run_file_performance_tests(self) -> Dict[str, Any]:
        """运行文件系统性能测试"""
        results = []

        # 文件创建性能测试
        file_create_result = self.test_file_creation()
        results.append(file_create_result)

        # 文件读取性能测试
        file_read_result = self.test_file_reading()
        results.append(file_read_result)

        # 文件复制性能测试
        file_copy_result = self.test_file_copying()
        results.append(file_copy_result)

        # 目录遍历性能测试
        dir_traversal_result = self.test_directory_traversal()
        results.append(dir_traversal_result)

        # 文件搜索性能测试
        file_search_result = self.test_file_searching()
        results.append(file_search_result)

        return {
            "success": True,
            "suite": "file",
            "results": results,
            "summary": self._generate_performance_summary(results)
        }

    def run_ai_performance_tests(self) -> Dict[str, Any]:
        """运行AI性能测试"""
        results = []

        # AI响应时间测试
        ai_response_result = self.test_ai_response_time()
        results.append(ai_response_result)

        # AI并发处理测试
        ai_concurrent_result = self.test_ai_concurrent_processing()
        results.append(ai_concurrent_result)

        # AI内存使用测试
        ai_memory_result = self.test_ai_memory_usage()
        results.append(ai_memory_result)

        # AI错误处理测试
        ai_error_result = self.test_ai_error_handling()
        results.append(ai_error_result)

        return {
            "success": True,
            "suite": "ai",
            "results": results,
            "summary": self._generate_performance_summary(results)
        }

    def run_ui_performance_tests(self) -> Dict[str, Any]:
        """运行用户界面性能测试"""
        results = []

        # UI响应时间测试
        ui_response_result = self.test_ui_response_time()
        results.append(ui_response_result)

        # UI渲染性能测试
        ui_render_result = self.test_ui_rendering()
        results.append(ui_render_result)

        # UI内存使用测试
        ui_memory_result = self.test_ui_memory_usage()
        results.append(ui_memory_result)

        # UI并发操作测试
        ui_concurrent_result = self.test_ui_concurrent_operations()
        results.append(ui_concurrent_result)

        return {
            "success": True,
            "suite": "ui",
            "results": results,
            "summary": self._generate_performance_summary(results)
        }

    def run_all_performance_tests(self) -> Dict[str, Any]:
        """运行所有性能测试"""
        all_results = {}

        # 运行各个测试套件
        suites = ["system", "file", "ai", "ui"]
        for suite in suites:
            result = self.run_performance_suite(suite)
            all_results[suite] = result

        return {
            "success": True,
            "suite": "all",
            "results": all_results,
            "summary": self._generate_overall_summary(all_results)
        }

    # ===== 系统性能测试 =====

    def test_cpu_performance(self) -> Dict[str, Any]:
        """测试CPU性能"""
        try:
            self.console.print("[bold blue]测试CPU性能...[/bold blue]")

            # 测试CPU密集型任务
            cpu_times = []
            start_time = time.time()

            for i in range(self.test_iterations):
                # CPU密集型计算
                result = 0
                for j in range(1000000):
                    result += j * j

                cpu_times.append(time.time() - start_time)
                start_time = time.time()

            # 计算统计信息
            avg_time = statistics.mean(cpu_times)
            max_time = max(cpu_times)
            min_time = min(cpu_times)

            # 获取CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            result = {
                "test": "cpu_performance",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "max_time": max_time,
                "min_time": min_time,
                "cpu_percent": cpu_percent,
                "throughput": self.test_iterations / sum(cpu_times),
                "status": "passed" if cpu_percent < self.baseline_metrics["cpu_threshold"] else "warning",
                "message": f"CPU使用率: {cpu_percent}%, 平均响应时间: {avg_time:.3f}秒"
            }

            self.console.print(f"[bold green]CPU性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"CPU性能测试失败: {str(e)}")
            return {
                "test": "cpu_performance",
                "error": str(e),
                "status": "failed"
            }

    def test_memory_performance(self) -> Dict[str, Any]:
        """测试内存性能"""
        try:
            self.console.print("[bold blue]测试内存性能...[/bold blue]")

            # 测试内存使用
            memory_usage = []
            start_memory = psutil.virtual_memory().used

            for i in range(self.test_iterations):
                # 创建大对象
                large_list = [0] * 1000000
                memory_usage.append(psutil.virtual_memory().used - start_memory)
                del large_list

            # 计算统计信息
            avg_memory = statistics.mean(memory_usage)
            max_memory = max(memory_usage)

            # 获取内存使用率
            memory_percent = psutil.virtual_memory().percent

            result = {
                "test": "memory_performance",
                "iterations": self.test_iterations,
                "avg_memory": avg_memory,
                "max_memory": max_memory,
                "memory_percent": memory_percent,
                "status": "passed" if memory_percent < self.baseline_metrics["memory_threshold"] else "warning",
                "message": f"内存使用率: {memory_percent}%, 平均内存使用: {avg_memory/1024/1024:.2f}MB"
            }

            self.console.print(f"[bold green]内存性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"内存性能测试失败: {str(e)}")
            return {
                "test": "memory_performance",
                "error": str(e),
                "status": "failed"
            }

    def test_disk_performance(self) -> Dict[str, Any]:
        """测试磁盘I/O性能"""
        try:
            self.console.print("[bold blue]测试磁盘I/O性能...[/bold blue]")

            # 测试文件读写性能
            write_times = []
            read_times = []

            for i in range(self.test_iterations):
                # 测试写入
                start_time = time.time()
                test_file = f"/tmp/test_{i}.txt"
                with open(test_file, 'w') as f:
                    f.write("x" * 10000)
                write_times.append(time.time() - start_time)

                # 测试读取
                start_time = time.time()
                with open(test_file, 'r') as f:
                    f.read()
                read_times.append(time.time() - start_time)

                # 清理文件
                os.remove(test_file)

            # 计算统计信息
            avg_write = statistics.mean(write_times)
            avg_read = statistics.mean(read_times)
            throughput = self.test_iterations / sum(write_times + read_times)

            result = {
                "test": "disk_performance",
                "iterations": self.test_iterations,
                "avg_write_time": avg_write,
                "avg_read_time": avg_read,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均写入时间: {avg_write:.3f}秒, 平均读取时间: {avg_read:.3f}秒, 吞吐量: {throughput:.2f}请求/秒"
            }

            self.console.print(f"[bold green]磁盘I/O性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"磁盘I/O性能测试失败: {str(e)}")
            return {
                "test": "disk_performance",
                "error": str(e),
                "status": "failed"
            }

    def test_network_performance(self) -> Dict[str, Any]:
        """测试网络性能"""
        try:
            self.console.print("[bold blue]测试网络性能...[/bold blue]")

            # 测试网络连接
            import socket
            start_time = time.time()

            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("8.8.8.8", 53))  # Google DNS
            sock.close()

            response_time = time.time() - start_time

            # 获取网络统计
            net_stats = psutil.net_io_counters()
            bytes_sent = net_stats.bytes_sent
            bytes_recv = net_stats.bytes_recv

            result = {
                "test": "network_performance",
                "response_time": response_time,
                "bytes_sent": bytes_sent,
                "bytes_recv": bytes_recv,
                "status": "passed" if response_time < self.baseline_metrics["response_time_threshold"] else "warning",
                "message": f"网络响应时间: {response_time:.3f}秒, 发送: {bytes_sent}字节, 接收: {bytes_recv}字节"
            }

            self.console.print(f"[bold green]网络性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"网络性能测试失败: {str(e)}")
            return {
                "test": "network_performance",
                "error": str(e),
                "status": "failed"
            }

    def test_process_creation(self) -> Dict[str, Any]:
        """测试进程创建性能"""
        try:
            self.console.print("[bold blue]测试进程创建性能...[/bold blue]")

            # 测试进程创建
            creation_times = []

            for i in range(min(self.test_iterations, 10)):  # 限制进程数量
                start_time = time.time()

                # 创建子进程
                import subprocess
                proc = subprocess.Popen(["echo", "test"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                proc.wait()

                creation_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(creation_times)
            throughput = len(creation_times) / sum(creation_times)

            result = {
                "test": "process_creation",
                "iterations": len(creation_times),
                "avg_time": avg_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均进程创建时间: {avg_time:.3f}秒, 吞吐量: {throughput:.2f}进程/秒"
            }

            self.console.print(f"[bold green]进程创建性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"进程创建性能测试失败: {str(e)}")
            return {
                "test": "process_creation",
                "error": str(e),
                "status": "failed"
            }

    # ===== 文件系统性能测试 =====

    def test_file_creation(self) -> Dict[str, Any]:
        """测试文件创建性能"""
        try:
            self.console.print("[bold blue]测试文件创建性能...[/bold blue]")

            # 创建临时目录
            temp_dir = "/tmp/perf_test"
            os.makedirs(temp_dir, exist_ok=True)

            # 测试文件创建
            creation_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 创建文件
                file_path = os.path.join(temp_dir, f"test_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write("x" * 1000)

                creation_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(creation_times)
            throughput = self.test_iterations / sum(creation_times)

            # 清理文件
            for i in range(self.test_iterations):
                file_path = os.path.join(temp_dir, f"test_{i}.txt")
                if os.path.exists(file_path):
                    os.remove(file_path)

            result = {
                "test": "file_creation",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均文件创建时间: {avg_time:.3f}秒, 吞吐量: {throughput:.2f}文件/秒"
            }

            self.console.print(f"[bold green]文件创建性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"文件创建性能测试失败: {str(e)}")
            return {
                "test": "file_creation",
                "error": str(e),
                "status": "failed"
            }

    def test_file_reading(self) -> Dict[str, Any]:
        """测试文件读取性能"""
        try:
            self.console.print("[bold blue]测试文件读取性能...[/bold blue]")

            # 创建临时目录和文件
            temp_dir = "/tmp/perf_test"
            os.makedirs(temp_dir, exist_ok=True)

            # 创建测试文件
            test_file = os.path.join(temp_dir, "large_file.txt")
            with open(test_file, 'w') as f:
                f.write("x" * 1000000)  # 1MB文件

            # 测试文件读取
            read_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 读取文件
                with open(test_file, 'r') as f:
                    f.read()

                read_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(read_times)
            throughput = self.test_iterations / sum(read_times)

            # 清理文件
            os.remove(test_file)

            result = {
                "test": "file_reading",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均文件读取时间: {avg_time:.3f}秒, 吞吐量: {throughput:.2f}文件/秒"
            }

            self.console.print(f"[bold green]文件读取性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"文件读取性能测试失败: {str(e)}")
            return {
                "test": "file_reading",
                "error": str(e),
                "status": "failed"
            }

    def test_file_copying(self) -> Dict[str, Any]:
        """测试文件复制性能"""
        try:
            self.console.print("[bold blue]测试文件复制性能...[/bold blue]")

            # 创建临时目录
            temp_dir = "/tmp/perf_test"
            os.makedirs(temp_dir, exist_ok=True)

            # 创建源文件
            source_file = os.path.join(temp_dir, "source.txt")
            with open(source_file, 'w') as f:
                f.write("x" * 1000000)  # 1MB文件

            # 测试文件复制
            copy_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 复制文件
                dest_file = os.path.join(temp_dir, f"dest_{i}.txt")
                shutil.copy2(source_file, dest_file)

                copy_times.append(time.time() - start_time)

                # 清理目标文件
                if os.path.exists(dest_file):
                    os.remove(dest_file)

            # 计算统计信息
            avg_time = statistics.mean(copy_times)
            throughput = self.test_iterations / sum(copy_times)

            # 清理源文件
            os.remove(source_file)

            result = {
                "test": "file_copying",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均文件复制时间: {avg_time:.3f}秒, 吞吐量: {throughput:.2f}文件/秒"
            }

            self.console.print(f"[bold green]文件复制性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"文件复制性能测试失败: {str(e)}")
            return {
                "test": "file_copying",
                "error": str(e),
                "status": "failed"
            }

    def test_directory_traversal(self) -> Dict[str, Any]:
        """测试目录遍历性能"""
        try:
            self.console.print("[bold blue]测试目录遍历性能...[/bold blue]")

            # 创建测试目录结构
            temp_dir = "/tmp/perf_test"
            os.makedirs(temp_dir, exist_ok=True)

            # 创建多层目录结构
            for i in range(10):
                subdir = os.path.join(temp_dir, f"level_{i}")
                os.makedirs(subdir, exist_ok=True)

                for j in range(100):
                    file_path = os.path.join(subdir, f"file_{j}.txt")
                    with open(file_path, 'w') as f:
                        f.write("x" * 100)

            # 测试目录遍历
            traversal_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 遍历目录
                file_count = 0
                for root, dirs, files in os.walk(temp_dir):
                    file_count += len(files)

                traversal_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(traversal_times)
            throughput = self.test_iterations / sum(traversal_times)

            # 清理目录
            shutil.rmtree(temp_dir)

            result = {
                "test": "directory_traversal",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均目录遍历时间: {avg_time:.3f}秒, 吞吐量: {throughput:.2f}次/秒"
            }

            self.console.print(f"[bold green]目录遍历性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"目录遍历性能测试失败: {str(e)}")
            return {
                "test": "directory_traversal",
                "error": str(e),
                "status": "failed"
            }

    def test_file_searching(self) -> Dict[str, Any]:
        """测试文件搜索性能"""
        try:
            self.console.print("[bold blue]测试文件搜索性能...[/bold blue]")

            # 创建测试目录结构
            temp_dir = "/tmp/perf_test"
            os.makedirs(temp_dir, exist_ok=True)

            # 创建大量文件
            for i in range(1000):
                file_path = os.path.join(temp_dir, f"file_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write("x" * 100)

                # 创建一些匹配的文件
                if i % 10 == 0:
                    file_path = os.path.join(temp_dir, f"match_{i}.txt")
                    with open(file_path, 'w') as f:
                        f.write("x" * 100)

            # 测试文件搜索
            search_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 搜索匹配的文件
                import glob
                matches = glob.glob(os.path.join(temp_dir, "match_*.txt"))

                search_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(search_times)
            throughput = self.test_iterations / sum(search_times)

            # 清理目录
            shutil.rmtree(temp_dir)

            result = {
                "test": "file_searching",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均文件搜索时间: {avg_time:.3f}秒, 吞吐量: {throughput:.2f}次/秒"
            }

            self.console.print(f"[bold green]文件搜索性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"文件搜索性能测试失败: {str(e)}")
            return {
                "test": "file_searching",
                "error": str(e),
                "status": "failed"
            }

    # ===== AI性能测试 =====

    def test_ai_response_time(self) -> Dict[str, Any]:
        """测试AI响应时间"""
        try:
            self.console.print("[bold blue]测试AI响应时间...[/bold blue]")

            # 模拟AI响应时间测试
            response_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 模拟AI处理
                time.sleep(0.1)  # 模拟AI处理时间

                response_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)

            result = {
                "test": "ai_response_time",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "max_time": max_time,
                "min_time": min_time,
                "status": "passed" if avg_time < self.baseline_metrics["response_time_threshold"] else "warning",
                "message": f"平均响应时间: {avg_time:.3f}秒, 最大响应时间: {max_time:.3f}秒, 最小响应时间: {min_time:.3f}秒"
            }

            self.console.print(f"[bold green]AI响应时间测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"AI响应时间测试失败: {str(e)}")
            return {
                "test": "ai_response_time",
                "error": str(e),
                "status": "failed"
            }

    def test_ai_concurrent_processing(self) -> Dict[str, Any]:
        """测试AI并发处理"""
        try:
            self.console.print("[bold blue]测试AI并发处理...[/bold blue]")

            # 模拟AI并发处理
            def simulate_ai_task(task_id):
                time.sleep(0.1)  # 模拟AI处理时间
                return task_id

            # 使用线程池进行并发处理
            start_time = time.time()

            with ThreadPoolExecutor(max_workers=self.test_concurrency) as executor:
                futures = [executor.submit(simulate_ai_task, i) for i in range(self.test_iterations)]

                # 等待所有任务完成
                for future in as_completed(futures):
                    try:
                        result = future.result()
                    except Exception as e:
                        logger.error(f"任务执行失败: {str(e)}")

            total_time = time.time() - start_time
            throughput = self.test_iterations / total_time

            result = {
                "test": "ai_concurrent_processing",
                "iterations": self.test_iterations,
                "concurrency": self.test_concurrency,
                "total_time": total_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"并发处理完成: {self.test_iterations}个任务, 耗时: {total_time:.3f}秒, 吞吐量: {throughput:.2f}任务/秒"
            }

            self.console.print(f"[bold green]AI并发处理测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"AI并发处理测试失败: {str(e)}")
            return {
                "test": "ai_concurrent_processing",
                "error": str(e),
                "status": "failed"
            }

    def test_ai_memory_usage(self) -> Dict[str, Any]:
        """测试AI内存使用"""
        try:
            self.console.print("[bold blue]测试AI内存使用...[/bold blue]")

            # 模拟AI内存使用
            initial_memory = psutil.Process().memory_info().rss

            # 创建大量AI相关对象
            ai_objects = []
            for i in range(1000):
                # 模拟AI对象
                obj = {
                    "id": i,
                    "data": "x" * 1000,  # 1KB数据
                    "embeddings": [0.1] * 100  # 100个浮点数
                }
                ai_objects.append(obj)

            # 获取内存使用
            peak_memory = psutil.Process().memory_info().rss
            memory_increase = peak_memory - initial_memory

            # 清理对象
            del ai_objects

            result = {
                "test": "ai_memory_usage",
                "objects_count": 1000,
                "memory_increase": memory_increase,
                "memory_increase_mb": memory_increase / 1024 / 1024,
                "status": "passed",
                "message": f"内存增加: {memory_increase/1024/1024:.2f}MB"
            }

            self.console.print(f"[bold green]AI内存使用测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"AI内存使用测试失败: {str(e)}")
            return {
                "test": "ai_memory_usage",
                "error": str(e),
                "status": "failed"
            }

    def test_ai_error_handling(self) -> Dict[str, Any]:
        """测试AI错误处理"""
        try:
            self.console.print("[bold blue]测试AI错误处理...[/bold blue]")

            # 模拟AI错误处理
            error_count = 0
            success_count = 0

            for i in range(self.test_iterations):
                try:
                    # 模拟AI处理，随机失败
                    if i % 10 == 0:
                        raise Exception("模拟AI错误")

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    logger.error(f"AI处理失败: {str(e)}")

            success_rate = success_count / self.test_iterations * 100

            result = {
                "test": "ai_error_handling",
                "iterations": self.test_iterations,
                "success_count": success_count,
                "error_count": error_count,
                "success_rate": success_rate,
                "status": "passed" if success_rate > 90 else "warning",
                "message": f"成功率: {success_rate:.1f}%, 成功: {success_count}, 失败: {error_count}"
            }

            self.console.print(f"[bold green]AI错误处理测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"AI错误处理测试失败: {str(e)}")
            return {
                "test": "ai_error_handling",
                "error": str(e),
                "status": "failed"
            }

    # ===== UI性能测试 =====

    def test_ui_response_time(self) -> Dict[str, Any]:
        """测试UI响应时间"""
        try:
            self.console.print("[bold blue]测试UI响应时间...[/bold blue]")

            # 模拟UI响应时间测试
            response_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 模拟UI处理
                time.sleep(0.05)  # 模拟UI处理时间

                response_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)

            result = {
                "test": "ui_response_time",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "max_time": max_time,
                "min_time": min_time,
                "status": "passed" if avg_time < 0.1 else "warning",
                "message": f"平均响应时间: {avg_time:.3f}秒, 最大响应时间: {max_time:.3f}秒, 最小响应时间: {min_time:.3f}秒"
            }

            self.console.print(f"[bold green]UI响应时间测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"UI响应时间测试失败: {str(e)}")
            return {
                "test": "ui_response_time",
                "error": str(e),
                "status": "failed"
            }

    def test_ui_rendering(self) -> Dict[str, Any]:
        """测试UI渲染性能"""
        try:
            self.console.print("[bold blue]测试UI渲染性能...[/bold blue]")

            # 模拟UI渲染
            render_times = []

            for i in range(self.test_iterations):
                start_time = time.time()

                # 模拟UI渲染
                time.sleep(0.02)  # 模拟渲染时间

                render_times.append(time.time() - start_time)

            # 计算统计信息
            avg_time = statistics.mean(render_times)
            throughput = self.test_iterations / sum(render_times)

            result = {
                "test": "ui_rendering",
                "iterations": self.test_iterations,
                "avg_time": avg_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"平均渲染时间: {avg_time:.3f}秒, 吞吐量: {throughput:.2f}帧/秒"
            }

            self.console.print(f"[bold green]UI渲染性能测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"UI渲染性能测试失败: {str(e)}")
            return {
                "test": "ui_rendering",
                "error": str(e),
                "status": "failed"
            }

    def test_ui_memory_usage(self) -> Dict[str, Any]:
        """测试UI内存使用"""
        try:
            self.console.print("[bold blue]测试UI内存使用...[/bold blue]")

            # 模拟UI内存使用
            initial_memory = psutil.Process().memory_info().rss

            # 创建大量UI相关对象
            ui_objects = []
            for i in range(1000):
                # 模拟UI组件
                obj = {
                    "id": i,
                    "type": "panel",
                    "content": "x" * 1000,  # 1KB内容
                    "children": []  # 子组件
                }
                ui_objects.append(obj)

            # 获取内存使用
            peak_memory = psutil.Process().memory_info().rss
            memory_increase = peak_memory - initial_memory

            # 清理对象
            del ui_objects

            result = {
                "test": "ui_memory_usage",
                "objects_count": 1000,
                "memory_increase": memory_increase,
                "memory_increase_mb": memory_increase / 1024 / 1024,
                "status": "passed",
                "message": f"内存增加: {memory_increase/1024/1024:.2f}MB"
            }

            self.console.print(f"[bold green]UI内存使用测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"UI内存使用测试失败: {str(e)}")
            return {
                "test": "ui_memory_usage",
                "error": str(e),
                "status": "failed"
            }

    def test_ui_concurrent_operations(self) -> Dict[str, Any]:
        """测试UI并发操作"""
        try:
            self.console.print("[bold blue]测试UI并发操作...[/bold blue]")

            # 模拟UI并发操作
            def simulate_ui_operation(op_id):
                time.sleep(0.05)  # 模拟UI操作时间
                return op_id

            # 使用线程池进行并发操作
            start_time = time.time()

            with ThreadPoolExecutor(max_workers=self.test_concurrency) as executor:
                futures = [executor.submit(simulate_ui_operation, i) for i in range(self.test_iterations)]

                # 等待所有操作完成
                for future in as_completed(futures):
                    try:
                        result = future.result()
                    except Exception as e:
                        logger.error(f"操作执行失败: {str(e)}")

            total_time = time.time() - start_time
            throughput = self.test_iterations / total_time

            result = {
                "test": "ui_concurrent_operations",
                "iterations": self.test_iterations,
                "concurrency": self.test_concurrency,
                "total_time": total_time,
                "throughput": throughput,
                "status": "passed",
                "message": f"并发操作完成: {self.test_iterations}个操作, 耗时: {total_time:.3f}秒, 吞吐量: {throughput:.2f}操作/秒"
            }

            self.console.print(f"[bold green]UI并发操作测试完成: {result['message']}[/bold green]")
            return result

        except Exception as e:
            logger.error(f"UI并发操作测试失败: {str(e)}")
            return {
                "test": "ui_concurrent_operations",
                "error": str(e),
                "status": "failed"
            }

    # ===== 辅助方法 =====

    def _generate_performance_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成性能测试摘要"""
        try:
            summary = {
                "total_tests": len(results),
                "passed_tests": sum(1 for r in results if r.get("status") == "passed"),
                "warning_tests": sum(1 for r in results if r.get("status") == "warning"),
                "failed_tests": sum(1 for r in results if r.get("status") == "failed"),
                "pass_rate": sum(1 for r in results if r.get("status") == "passed") / len(results) * 100 if results else 0
            }

            # 计算平均响应时间
            response_times = [r.get("avg_time", 0) for r in results if "avg_time" in r]
            if response_times:
                summary["avg_response_time"] = statistics.mean(response_times)

            # 计算平均吞吐量
            throughputs = [r.get("throughput", 0) for r in results if "throughput" in r]
            if throughputs:
                summary["avg_throughput"] = statistics.mean(throughputs)

            return summary

        except Exception as e:
            logger.error(f"生成性能摘要失败: {str(e)}")
            return {
                "error": str(e)
            }

    def _generate_overall_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成整体性能摘要"""
        try:
            overall_summary = {
                "total_suites": len(all_results),
                "passed_suites": sum(1 for r in all_results.values() if r.get("success")),
                "failed_suites": sum(1 for r in all_results.values() if not r.get("success")),
                "overall_success_rate": sum(1 for r in all_results.values() if r.get("success")) / len(all_results) * 100 if all_results else 0
            }

            # 汇总所有测试结果
            all_test_results = []
            for suite_result in all_results.values():
                if suite_result.get("success") and "results" in suite_result:
                    all_test_results.extend(suite_result["results"])

            overall_summary["total_tests"] = len(all_test_results)
            overall_summary["passed_tests"] = sum(1 for r in all_test_results if r.get("status") == "passed")
            overall_summary["warning_tests"] = sum(1 for r in all_test_results if r.get("status") == "warning")
            overall_summary["failed_tests"] = sum(1 for r in all_test_results if r.get("status") == "failed")
            overall_summary["overall_pass_rate"] = overall_summary["passed_tests"] / overall_summary["total_tests"] * 100 if overall_summary["total_tests"] > 0 else 0

            return overall_summary

        except Exception as e:
            logger.error(f"生成整体摘要失败: {str(e)}")
            return {
                "error": str(e)
            }
