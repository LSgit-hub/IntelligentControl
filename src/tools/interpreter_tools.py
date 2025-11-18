#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
解释器工具模块
提供多种编程语言解释器的包装功能
"""

import os
import sys
import subprocess
import tempfile
import shlex
from typing import Dict, Any, List, Optional

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class InterpreterTools:
    """解释器工具类"""

    def __init__(self):
        """初始化解释器工具"""
        self.interpreters = {
            'python': self._get_python_path(),
            'node': self._get_node_path(),
            'powershell': self._get_powershell_path(),
            'bash': self._get_bash_path(),
            'ruby': 'ruby',
            'perl': 'perl',
            'lua': 'lua'
        }

        # 支持的文件扩展名
        self.extensions = {
            'python': ['.py'],
            'node': ['.js', '.mjs'],
            'powershell': ['.ps1'],
            'bash': ['.sh'],
            'ruby': ['.rb'],
            'perl': ['.pl'],
            'lua': ['.lua']
        }

    def _get_python_path(self) -> str:
        """获取Python解释器路径"""
        # 尝试从环境变量获取
        python_path = os.getenv('PYTHON', None)
        if python_path and os.path.exists(python_path):
            return python_path

        # 尝试常见路径
        for python_name in ['python', 'python3', 'python3.9', 'python3.8', 'python3.7']:
            try:
                result = subprocess.run(
                    [python_name, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return python_name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        # 默认返回python
        return 'python'

    def _get_node_path(self) -> str:
        """获取Node.js解释器路径"""
        # 尝试从环境变量获取
        node_path = os.getenv('NODE', None)
        if node_path and os.path.exists(node_path):
            return node_path

        # 尝试常见路径
        for node_name in ['node', 'nodejs']:
            try:
                result = subprocess.run(
                    [node_name, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return node_name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        # 默认返回node
        return 'node'

    def _get_powershell_path(self) -> str:
        """获取PowerShell解释器路径"""
        # 尝试从环境变量获取
        pwsh_path = os.getenv('POWERSHELL', None)
        if pwsh_path and os.path.exists(pwsh_path):
            return pwsh_path

        # 尝试常见路径
        for pwsh_name in ['powershell', 'pwsh']:
            try:
                result = subprocess.run(
                    [pwsh_name, '-Command', '$PSVersionTable.PSVersion'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return pwsh_name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        # 默认返回powershell
        return 'powershell'

    def _get_bash_path(self) -> str:
        """获取Bash解释器路径"""
        # 尝试从环境变量获取
        bash_path = os.getenv('BASH', None)
        if bash_path and os.path.exists(bash_path):
            return bash_path

        # 尝试常见路径
        for bash_name in ['bash', 'sh']:
            try:
                result = subprocess.run(
                    [bash_name, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return bash_name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        # 默认返回bash
        return 'bash'

    def execute_code(self, language: str, code: str, timeout: int = 30) -> Dict[str, Any]:
        """
        执行指定语言的代码并返回结果

        参数:
            language: 编程语言名称
            code: 要执行的代码
            timeout: 超时时间（秒）

        返回:
            包含执行结果的字典
        """
        # 检查语言是否支持
        if language.lower() not in self.interpreters:
            return {"error": f"不支持的编程语言: {language}"}

        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=f'.{language}', 
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            logger.info(f"执行{language}代码: {temp_file_path}")

            # 根据不同语言选择执行方式
            interpreter = self.interpreters[language.lower()]

            if language.lower() == 'powershell':
                cmd = f'{interpreter} -ExecutionPolicy Bypass -File "{temp_file_path}"'
            elif language.lower() == 'bash':
                cmd = f'"{interpreter}" "{temp_file_path}"'
            else:
                cmd = f'{interpreter} "{temp_file_path}"'

            # 执行代码
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # 清理临时文件
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "language": language
            }
        except subprocess.TimeoutExpired:
            error_msg = f"{language}代码执行超时: {timeout}秒"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"{language}代码执行失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def execute_file(self, file_path: str, timeout: int = 30) -> Dict[str, Any]:
        """
        执行指定文件中的代码

        参数:
            file_path: 文件路径
            timeout: 超时时间（秒）

        返回:
            包含执行结果的字典
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {"error": f"文件不存在: {file_path}"}

        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # 查找对应的语言
        language = None
        for lang, extensions in self.extensions.items():
            if ext in extensions:
                language = lang
                break

        if not language:
            return {"error": f"不支持的文件类型: {ext}"}

        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return {"error": f"读取文件失败: {str(e)}"}

        # 执行代码
        return self.execute_code(language, code, timeout)

    def get_supported_languages(self) -> List[str]:
        """获取支持的编程语言列表"""
        return list(self.interpreters.keys())

    def get_supported_extensions(self) -> Dict[str, List[str]]:
        """获取支持的文件扩展名"""
        return self.extensions

    def detect_language(self, file_path: str) -> Optional[str]:
        """
        根据文件扩展名检测语言

        参数:
            file_path: 文件路径

        返回:
            检测到的语言名称，如果无法检测则返回None
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return None

        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # 查找对应的语言
        for lang, extensions in self.extensions.items():
            if ext in extensions:
                return lang

        return None
