#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试运行器模块
运行所有测试并生成综合报告
"""

import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live

from .test_framework import TestFramework
from .test_cases import TestCases
from .performance_tests import PerformanceTests
from .optimization import SystemOptimizer
from utils.logger import setup_logger

logger = setup_logger(__name__)

class TestRunner:
    """测试运行器类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化测试运行器

        参数:
            config: 配置信息
        """
        self.config = config
        self.console = Console()

        # 初始化测试组件
        self.test_framework = TestFramework(config)
        self.test_cases = TestCases()
        self.performance_tests = PerformanceTests(config)
        self.optimizer = SystemOptimizer(config)

        # 测试结果
        self.test_results = {}
        self.performance_results = {}
        self.optimization_results = {}

        # 运行状态
        self.running = False
        self.start_time = None
        self.end_time = None

    def run_all_tests(self) -> Dict[str, Any]:
        """
        运行所有测试

        返回:
            测试结果
        """
        try:
            self.console.print("[bold blue]开始运行所有测试...[/bold blue]")
            self.start_time = time.time()

            # 运行功能测试
            self.console.print("[bold green]运行功能测试...[/bold green]")
            functional_results = self.run_functional_tests()

            # 运行性能测试
            self.console.print("[bold green]运行性能测试...[/bold green]")
            performance_results = self.run_performance_tests()

            # 运行优化
            self.console.print("[bold green]运行系统优化...[/bold green]")
            optimization_results = self.run_optimization(performance_results)

            # 生成综合报告
            self.end_time = time.time()
            report = self.generate_comprehensive_report(
                functional_results, 
                performance_results, 
                optimization_results
            )

            self.console.print("[bold green]所有测试运行完成[/bold green]")

            return {
                "success": True,
                "report": report,
                "functional_results": functional_results,
                "performance_results": performance_results,
                "optimization_results": optimization_results,
                "duration": self.end_time - self.start_time
            }

        except Exception as e:
            logger.error(f"运行所有测试失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def run_functional_tests(self) -> Dict[str, Any]:
        """
        运行功能测试

        返回:
            功能测试结果
        """
        test_suites = ["system", "file", "ai", "ui"]
        results = {}

        for suite in test_suites:
            try:
                result = self.test_framework.run_test_suite(suite)
                results[suite] = result

                if result.get("success"):
                    stats = result.get("stats", {})
                    self.console.print(f"[bold green]{suite}测试完成: 通过 {stats.get('passed', 0)}/{stats.get('total', 0)}[/bold green]")
                else:
                    self.console.print(f"[bold red]{suite}测试失败: {result.get('error', '未知错误')}[/bold red]")

            except Exception as e:
                logger.error(f"运行{suite}测试失败: {str(e)}")
                results[suite] = {
                    "success": False,
                    "error": str(e)
                }

        return results

    def run_performance_tests(self) -> Dict[str, Any]:
        """
        运行性能测试

        返回:
            性能测试结果
        """
        test_suites = ["system", "file", "ai", "ui"]
        results = {}

        for suite in test_suites:
            try:
                result = self.performance_tests.run_performance_suite(suite)
                results[suite] = result

                if result.get("success"):
                    summary = result.get("summary", {})
                    self.console.print(f"[bold green]{suite}性能测试完成: {summary.get('status', '未知')}[/bold green]")
                else:
                    self.console.print(f"[bold red]{suite}性能测试失败: {result.get('error', '未知错误')}[/bold red]")

            except Exception as e:
                logger.error(f"运行{suite}性能测试失败: {str(e)}")
                results[suite] = {
                    "success": False,
                    "error": str(e)
                }

        return results

    def run_optimization(self, performance_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行系统优化

        参数:
            performance_results: 性能测试结果

        返回:
            优化结果
        """
        try:
            # 合并性能测试结果
            combined_results = {}
            for suite, result in performance_results.items():
                if result.get("success"):
                    combined_results.update(result.get("results", {}))

            # 运行优化
            optimization_result = self.optimizer.run_optimization_suite(combined_results)

            if optimization_result.get("success"):
                optimizations = optimization_result.get("optimizations", [])
                self.console.print(f"[bold green]系统优化完成: 应用了 {len(optimizations)} 项优化[/bold green]")
            else:
                self.console.print(f"[bold red]系统优化失败: {optimization_result.get('error', '未知错误')}[/bold red]")

            return optimization_result

        except Exception as e:
            logger.error(f"运行系统优化失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def generate_comprehensive_report(self, functional_results: Dict[str, Any], 
                                    performance_results: Dict[str, Any], 
                                    optimization_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合测试报告

        参数:
            functional_results: 功能测试结果
            performance_results: 性能测试结果
            optimization_results: 优化结果

        返回:
            综合报告
        """
        try:
            # 计算总体统计
            total_functional_tests = 0
            passed_functional_tests = 0
            failed_functional_tests = 0

            for suite, result in functional_results.items():
                if result.get("success"):
                    stats = result.get("stats", {})
                    total_functional_tests += stats.get("total", 0)
                    passed_functional_tests += stats.get("passed", 0)
                    failed_functional_tests += stats.get("failed", 0)

            # 生成报告内容
            report_content = f"""# 智能控制系统 - 综合测试报告

## 测试概览
- **测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **测试耗时**: {self.end_time - self.start_time:.2f} 秒
- **功能测试**: 通过 {passed_functional_tests}/{total_functional_tests} ({passed_functional_tests/total_functional_tests*100:.1f}%)
- **性能测试**: 完成 {len(performance_results)} 个套件
- **系统优化**: {len(optimization_results.get('optimizations', []))} 项优化

## 功能测试结果
"""

            # 添加功能测试结果
            for suite, result in functional_results.items():
                if result.get("success"):
                    stats = result.get("stats", {})
                    report_content += f"- **{suite}**: {stats.get('passed', 0)}/{stats.get('total', 0)} 通过
"
                else:
                    report_content += f"- **{suite}**: 失败 - {result.get('error', '未知错误')}
"

            report_content += "
## 性能测试结果
"

            # 添加性能测试结果
            for suite, result in performance_results.items():
                if result.get("success"):
                    summary = result.get('summary', {})
                    report_content += f"- **{suite}**: {summary.get('status', '未知')}
"
                else:
                    report_content += f"- **{suite}**: 失败 - {result.get('error', '未知错误')}
"

            report_content += "
## 优化结果
"

            # 添加优化结果
            if optimization_results.get("success"):
                optimizations = optimization_results.get('optimizations', [])
                for opt in optimizations:
                    report_content += f"- **{opt.get('type', '未知')}**: {opt.get('status', '未知')}
"
            else:
                report_content += f"- **优化失败**: {optimization_results.get('error', '未知错误')}
"

            # 添加建议
            report_content += "
## 改进建议
"
            report_content += "- 定期运行性能测试监控系统状态
"
            report_content += "- 根据测试结果调整系统配置
"
            report_content += "- 关注资源使用情况及时优化
"
            report_content += "- 保持系统更新以获得最佳性能
"

            # 保存报告
            report_file = os.path.join(
                self.config.get("report_dir", os.path.expanduser("~/.intelligent_control/reports")),
                f"comprehensive_report_{time.strftime('%Y%m%d_%H%M%S')}.md"
            )

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)

            return {
                "success": True,
                "report_content": report_content,
                "report_file": report_file,
                "stats": {
                    "total_functional_tests": total_functional_tests,
                    "passed_functional_tests": passed_functional_tests,
                    "failed_functional_tests": failed_functional_tests,
                    "performance_suites": len(performance_results),
                    "optimizations_applied": len(optimization_results.get('optimizations', []))
                }
            }

        except Exception as e:
            logger.error(f"生成综合报告失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def run_single_test(self, test_type: str, test_name: str) -> Dict[str, Any]:
        """
        运行单个测试

        参数:
            test_type: 测试类型 (functional, performance, optimization)
            test_name: 测试名称

        返回:
            测试结果
        """
        try:
            self.console.print(f"[bold blue]开始运行 {test_type} 测试: {test_name}[/bold blue]")

            if test_type == "functional":
                result = self.test_framework.run_test_suite(test_name)
            elif test_type == "performance":
                result = self.performance_tests.run_performance_suite(test_name)
            elif test_type == "optimization":
                # 对于优化测试，需要先有性能测试结果
                if not self.performance_results:
                    self.console.print("[bold red]优化测试需要先运行性能测试[/bold red]")
                    return {"success": False, "error": "需要先运行性能测试"}
                result = self.optimizer.run_optimization_suite(self.performance_results)
            else:
                return {"success": False, "error": f"未知的测试类型: {test_type}"}

            if result.get("success"):
                self.console.print(f"[bold green]{test_type} 测试完成[/bold green]")
            else:
                self.console.print(f"[bold red]{test_type} 测试失败: {result.get('error', '未知错误')}[/bold red]")

            return result

        except Exception as e:
            logger.error(f"运行 {test_type} 测试失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def display_results(self, results: Dict[str, Any]) -> None:
        """
        显示测试结果

        参数:
            results: 测试结果
        """
        try:
            if results.get("success"):
                report = results.get("report", {})
                stats = report.get("stats", {})

                # 显示统计信息
                table = Table(title="测试统计")
                table.add_column("项目", style="cyan")
                table.add_column("数值", style="green")

                table.add_row("功能测试总数", str(stats.get("total_functional_tests", 0)))
                table.add_row("通过测试数", str(stats.get("passed_functional_tests", 0)))
                table.add_row("失败测试数", str(stats.get("failed_functional_tests", 0)))
                table.add_row("性能测试套件", str(stats.get("performance_suites", 0)))
                table.add_row("应用优化数", str(stats.get("optimizations_applied", 0)))
                table.add_row("测试耗时", f"{results.get('duration', 0):.2f} 秒")

                self.console.print(table)

                # 显示报告
                report_content = report.get("report_content", "")
                if report_content:
                    markdown = Markdown(report_content)
                    self.console.print(Panel(markdown, title="测试报告", border_style="blue"))

            else:
                self.console.print(f"[bold red]测试失败: {results.get('error', '未知错误')}[/bold red]")

        except Exception as e:
            logger.error(f"显示测试结果失败: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能控制系统测试运行器")
    parser.add_argument("--type", choices=["functional", "performance", "optimization", "all"], 
                       default="all", help="测试类型")
    parser.add_argument("--suite", help="测试套件名称")
    parser.add_argument("--config", help="配置文件路径")

    args = parser.parse_args()

    # 默认配置
    config = {
        "test_dir": os.path.expanduser("~/.intelligent_control/tests"),
        "report_dir": os.path.expanduser("~/.intelligent_control/reports"),
        "enable_cpu_optimization": True,
        "enable_memory_optimization": True,
        "enable_disk_optimization": True,
        "enable_network_optimization": True
    }

    # 加载配置文件
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r', encoding='utf-8') as f:
            config.update(json.load(f))

    # 创建测试运行器
    runner = TestRunner(config)

    # 运行测试
    if args.type == "all":
        results = runner.run_all_tests()
    elif args.type == "functional":
        results = runner.run_functional_tests()
    elif args.type == "performance":
        results = runner.run_performance_tests()
    elif args.type == "optimization":
        results = runner.run_optimization({})
    else:
        results = {"success": False, "error": "未知的测试类型"}

    # 显示结果
    runner.display_results(results)

    return 0 if results.get("success") else 1

if __name__ == "__main__":
    sys.exit(main())
