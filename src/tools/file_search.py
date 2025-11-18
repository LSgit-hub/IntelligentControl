#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件搜索工具模块
提供高级文件搜索功能
"""

import os
import fnmatch
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class FileSearch:
    """文件搜索类"""

    def __init__(self):
        """初始化文件搜索"""
        self.current_dir = os.getcwd()

    def find_files(
        self, 
        pattern: str = "*", 
        path: str = ".", 
        recursive: bool = True,
        case_sensitive: bool = False,
        full_path: bool = False
    ) -> Dict[str, Any]:
        """
        查找文件

        参数:
            pattern: 文件匹配模式（支持通配符）
            path: 搜索路径
            recursive: 是否递归搜索子目录
            case_sensitive: 是否区分大小写
            full_path: 是否返回完整路径

        返回:
            搜索结果
        """
        try:
            search_path = Path(path).resolve()

            # 检查路径是否存在
            if not search_path.exists():
                return {"error": f"路径不存在: {search_path}"}

            # 检查路径是否为目录
            if not search_path.is_dir():
                return {"error": f"路径不是目录: {search_path}"}

            # 搜索文件
            matches = []

            if recursive:
                # 递归搜索
                for root, _, files in os.walk(search_path):
                    for file in fnmatch.filter(files, pattern):
                        file_path = Path(root) / file
                        matches.append(str(file_path) if full_path else file)
            else:
                # 仅搜索当前目录
                for file in os.listdir(search_path):
                    file_path = search_path / file
                    if file_path.is_file() and fnmatch.fnmatch(file, pattern):
                        matches.append(str(file_path) if full_path else file)

            logger.info(f"查找文件: 在 {search_path} 中找到 {len(matches)} 个匹配项")

            return {
                "success": True,
                "pattern": pattern,
                "path": str(search_path),
                "recursive": recursive,
                "case_sensitive": case_sensitive,
                "full_path": full_path,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            error_msg = f"查找文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def find_files_by_regex(
        self, 
        regex: str, 
        path: str = ".", 
        recursive: bool = True,
        case_sensitive: bool = False,
        full_path: bool = False
    ) -> Dict[str, Any]:
        """
        使用正则表达式查找文件

        参数:
            regex: 正则表达式
            path: 搜索路径
            recursive: 是否递归搜索子目录
            case_sensitive: 是否区分大小写
            full_path: 是否返回完整路径

        返回:
            搜索结果
        """
        try:
            search_path = Path(path).resolve()

            # 检查路径是否存在
            if not search_path.exists():
                return {"error": f"路径不存在: {search_path}"}

            # 检查路径是否为目录
            if not search_path.is_dir():
                return {"error": f"路径不是目录: {search_path}"}

            # 编译正则表达式
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(regex, flags)

            # 搜索文件
            matches = []

            if recursive:
                # 递归搜索
                for root, _, files in os.walk(search_path):
                    for file in files:
                        if pattern.search(file):
                            file_path = Path(root) / file
                            matches.append(str(file_path) if full_path else file)
            else:
                # 仅搜索当前目录
                for file in os.listdir(search_path):
                    file_path = search_path / file
                    if file_path.is_file() and pattern.search(file):
                        matches.append(str(file_path) if full_path else file)

            logger.info(f"正则查找文件: 在 {search_path} 中找到 {len(matches)} 个匹配项")

            return {
                "success": True,
                "regex": regex,
                "path": str(search_path),
                "recursive": recursive,
                "case_sensitive": case_sensitive,
                "full_path": full_path,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            error_msg = f"正则查找文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def find_files_by_content(
        self, 
        content: str, 
        path: str = ".", 
        recursive: bool = True,
        case_sensitive: bool = False,
        full_path: bool = False,
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        按内容查找文件

        参数:
            content: 要查找的内容
            path: 搜索路径
            recursive: 是否递归搜索子目录
            case_sensitive: 是否区分大小写
            full_path: 是否返回完整路径
            encoding: 文件编码

        返回:
            搜索结果
        """
        try:
            search_path = Path(path).resolve()

            # 检查路径是否存在
            if not search_path.exists():
                return {"error": f"路径不存在: {search_path}"}

            # 检查路径是否为目录
            if not search_path.is_dir():
                return {"error": f"路径不是目录: {search_path}"}

            # 搜索文件
            matches = []
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(re.escape(content), flags)

            if recursive:
                # 递归搜索
                for root, _, files in os.walk(search_path):
                    for file in files:
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                                file_content = f.read()
                                if pattern.search(file_content):
                                    matches.append(str(file_path) if full_path else file)
                        except Exception:
                            continue
            else:
                # 仅搜索当前目录
                for file in os.listdir(search_path):
                    file_path = search_path / file
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                                file_content = f.read()
                                if pattern.search(file_content):
                                    matches.append(str(file_path) if full_path else file)
                        except Exception:
                            continue

            logger.info(f"按内容查找文件: 在 {search_path} 中找到 {len(matches)} 个匹配项")

            return {
                "success": True,
                "content": content,
                "path": str(search_path),
                "recursive": recursive,
                "case_sensitive": case_sensitive,
                "full_path": full_path,
                "encoding": encoding,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            error_msg = f"按内容查找文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def find_files_by_size(
        self, 
        min_size: Optional[int] = None, 
        max_size: Optional[int] = None, 
        path: str = ".", 
        recursive: bool = True,
        full_path: bool = False
    ) -> Dict[str, Any]:
        """
        按大小查找文件

        参数:
            min_size: 最小文件大小（字节）
            max_size: 最大文件大小（字节）
            path: 搜索路径
            recursive: 是否递归搜索子目录
            full_path: 是否返回完整路径

        返回:
            搜索结果
        """
        try:
            search_path = Path(path).resolve()

            # 检查路径是否存在
            if not search_path.exists():
                return {"error": f"路径不存在: {search_path}"}

            # 检查路径是否为目录
            if not search_path.is_dir():
                return {"error": f"路径不是目录: {search_path}"}

            # 搜索文件
            matches = []

            if recursive:
                # 递归搜索
                for root, _, files in os.walk(search_path):
                    for file in files:
                        file_path = Path(root) / file
                        try:
                            size = file_path.stat().st_size
                            if (min_size is None or size >= min_size) and (max_size is None or size <= max_size):
                                matches.append((str(file_path) if full_path else file, size))
                        except Exception:
                            continue
            else:
                # 仅搜索当前目录
                for file in os.listdir(search_path):
                    file_path = search_path / file
                    if file_path.is_file():
                        try:
                            size = file_path.stat().st_size
                            if (min_size is None or size >= min_size) and (max_size is None or size <= max_size):
                                matches.append((str(file_path) if full_path else file, size))
                        except Exception:
                            continue

            # 按大小排序
            matches.sort(key=lambda x: x[1])

            # 只保留文件名
            file_matches = [match[0] for match in matches]

            logger.info(f"按大小查找文件: 在 {search_path} 中找到 {len(file_matches)} 个匹配项")

            return {
                "success": True,
                "min_size": min_size,
                "max_size": max_size,
                "path": str(search_path),
                "recursive": recursive,
                "full_path": full_path,
                "matches": file_matches,
                "count": len(file_matches)
            }
        except Exception as e:
            error_msg = f"按大小查找文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def find_files_by_extension(
        self, 
        extensions: Union[str, List[str]], 
        path: str = ".", 
        recursive: bool = True,
        full_path: bool = False
    ) -> Dict[str, Any]:
        """
        按扩展名查找文件

        参数:
            extensions: 文件扩展名或扩展名列表
            path: 搜索路径
            recursive: 是否递归搜索子目录
            full_path: 是否返回完整路径

        返回:
            搜索结果
        """
        try:
            search_path = Path(path).resolve()

            # 检查路径是否存在
            if not search_path.exists():
                return {"error": f"路径不存在: {search_path}"}

            # 检查路径是否为目录
            if not search_path.is_dir():
                return {"error": f"路径不是目录: {search_path}"}

            # 规范化扩展名
            if isinstance(extensions, str):
                extensions = [extensions]

            # 添加点前缀（如果需要）
            normalized_extensions = []
            for ext in extensions:
                if not ext.startswith('.'):
                    ext = '.' + ext
                normalized_extensions.append(ext.lower())

            # 搜索文件
            matches = []

            if recursive:
                # 递归搜索
                for root, _, files in os.walk(search_path):
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.suffix.lower() in normalized_extensions:
                            matches.append(str(file_path) if full_path else file)
            else:
                # 仅搜索当前目录
                for file in os.listdir(search_path):
                    file_path = search_path / file
                    if file_path.is_file() and file_path.suffix.lower() in normalized_extensions:
                        matches.append(str(file_path) if full_path else file)

            logger.info(f"按扩展名查找文件: 在 {search_path} 中找到 {len(matches)} 个匹配项")

            return {
                "success": True,
                "extensions": extensions,
                "path": str(search_path),
                "recursive": recursive,
                "full_path": full_path,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            error_msg = f"按扩展名查找文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def find_files_by_modified_time(
        self, 
        min_time: Optional[float] = None, 
        max_time: Optional[float] = None, 
        path: str = ".", 
        recursive: bool = True,
        full_path: bool = False
    ) -> Dict[str, Any]:
        """
        按修改时间查找文件

        参数:
            min_time: 最小修改时间（时间戳）
            max_time: 最大修改时间（时间戳）
            path: 搜索路径
            recursive: 是否递归搜索子目录
            full_path: 是否返回完整路径

        返回:
            搜索结果
        """
        try:
            search_path = Path(path).resolve()

            # 检查路径是否存在
            if not search_path.exists():
                return {"error": f"路径不存在: {search_path}"}

            # 检查路径是否为目录
            if not search_path.is_dir():
                return {"error": f"路径不是目录: {search_path}"}

            # 搜索文件
            matches = []

            if recursive:
                # 递归搜索
                for root, _, files in os.walk(search_path):
                    for file in files:
                        file_path = Path(root) / file
                        try:
                            modified_time = file_path.stat().st_mtime
                            if (min_time is None or modified_time >= min_time) and (max_time is None or modified_time <= max_time):
                                matches.append((str(file_path) if full_path else file, modified_time))
                        except Exception:
                            continue
            else:
                # 仅搜索当前目录
                for file in os.listdir(search_path):
                    file_path = search_path / file
                    if file_path.is_file():
                        try:
                            modified_time = file_path.stat().st_mtime
                            if (min_time is None or modified_time >= min_time) and (max_time is None or modified_time <= max_time):
                                matches.append((str(file_path) if full_path else file, modified_time))
                        except Exception:
                            continue

            # 按修改时间排序
            matches.sort(key=lambda x: x[1])

            # 只保留文件名
            file_matches = [match[0] for match in matches]

            logger.info(f"按修改时间查找文件: 在 {search_path} 中找到 {len(file_matches)} 个匹配项")

            return {
                "success": True,
                "min_time": min_time,
                "max_time": max_time,
                "path": str(search_path),
                "recursive": recursive,
                "full_path": full_path,
                "matches": file_matches,
                "count": len(file_matches)
            }
        except Exception as e:
            error_msg = f"按修改时间查找文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
