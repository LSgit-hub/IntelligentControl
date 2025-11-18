#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件比较工具模块
提供文件和目录比较功能
"""

import os
import difflib
import filecmp
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class FileComparator:
    """文件比较器类"""

    def __init__(self):
        """初始化文件比较器"""
        self.current_dir = os.getcwd()

    def compare_files(
        self, 
        file1: str, 
        file2: str, 
        show_diff: bool = False,
        encoding: str = "utf-8",
        ignore_whitespace: bool = False
    ) -> Dict[str, Any]:
        """
        比较两个文件

        参数:
            file1: 第一个文件路径
            file2: 第二个文件路径
            show_diff: 是否显示差异
            encoding: 文件编码
            ignore_whitespace: 是否忽略空白字符

        返回:
            比较结果
        """
        try:
            path1 = Path(file1).resolve()
            path2 = Path(file2).resolve()

            # 检查文件是否存在
            if not path1.exists():
                return {"error": f"文件不存在: {path1}"}

            if not path2.exists():
                return {"error": f"文件不存在: {path2}"}

            # 检查是否为文件
            if not path1.is_file():
                return {"error": f"路径不是文件: {path1}"}

            if not path2.is_file():
                return {"error": f"路径不是文件: {path2}"}

            # 比较文件
            result = filecmp.cmp(str(path1), str(path2), shallow=False)

            # 如果需要显示差异
            diff = None
            if show_diff and not result:
                try:
                    with open(path1, 'r', encoding=encoding, errors='ignore') as f1:
                        with open(path2, 'r', encoding=encoding, errors='ignore') as f2:
                            text1 = f1.readlines()
                            text2 = f2.readlines()

                            # 生成差异
                            if ignore_whitespace:
                                # 忽略空白字符
                                text1 = [line.strip() for line in text1]
                                text2 = [line.strip() for line in text2]

                            diff = difflib.unified_diff(
                                text1, text2,
                                fromfile=str(path1),
                                tofile=str(path2),
                                lineterm=""
                            )
                except Exception as e:
                    logger.warning(f"无法生成差异: {str(e)}")

            logger.info(f"比较文件: {path1} vs {path2}")

            return {
                "success": True,
                "file1": str(path1),
                "file2": str(path2),
                "equal": result,
                "show_diff": show_diff,
                "ignore_whitespace": ignore_whitespace,
                "diff": list(diff) if diff else None
            }
        except Exception as e:
            error_msg = f"比较文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def compare_directories(
        self, 
        dir1: str, 
        dir2: str, 
        show_diff: bool = False,
        ignore_hidden: bool = True
    ) -> Dict[str, Any]:
        """
        比较两个目录

        参数:
            dir1: 第一个目录路径
            dir2: 第二个目录路径
            show_diff: 是否显示差异
            ignore_hidden: 是否忽略隐藏文件

        返回:
            比较结果
        """
        try:
            path1 = Path(dir1).resolve()
            path2 = Path(dir2).resolve()

            # 检查目录是否存在
            if not path1.exists():
                return {"error": f"目录不存在: {path1}"}

            if not path2.exists():
                return {"error": f"目录不存在: {path2}"}

            # 检查是否为目录
            if not path1.is_dir():
                return {"error": f"路径不是目录: {path1}"}

            if not path2.is_dir():
                return {"error": f"路径不是目录: {path2}"}

            # 比较目录
            comparison = filecmp.dircmp(str(path1), str(path2), ignore_hidden=ignore_hidden)

            # 准备结果
            result = {
                "success": True,
                "dir1": str(path1),
                "dir2": str(path2),
                "ignore_hidden": ignore_hidden,
                "left_only": sorted(comparison.left_only),
                "right_only": sorted(comparison.right_only),
                "common": sorted(comparison.common),
                "common_dirs": sorted(comparison.common_dirs),
                "common_files": sorted(comparison.common_files),
                "common_funny": sorted(comparison.common_funny),
                "same_files": sorted(comparison.same_files),
                "diff_files": sorted(comparison.diff_files),
                " funny_files": sorted(comparison.funny_files)
            }

            # 如果需要显示差异
            if show_diff and result["diff_files"]:
                diff_details = []
                for file in result["diff_files"]:
                    file1 = path1 / file
                    file2 = path2 / file

                    # 比较文件
                    file_result = self.compare_files(str(file1), str(file2), show_diff=False)
                    diff_details.append({
                        "file": file,
                        "equal": file_result["equal"]
                    })

                result["diff_details"] = diff_details

            logger.info(f"比较目录: {path1} vs {path2}")

            return result
        except Exception as e:
            error_msg = f"比较目录失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def find_duplicate_files(
        self, 
        path: str, 
        recursive: bool = True,
        compare_content: bool = True
    ) -> Dict[str, Any]:
        """
        查找重复文件

        参数:
            path: 搜索路径
            recursive: 是否递归搜索子目录
            compare_content: 是否比较文件内容（而不仅仅是大小）

        返回:
            重复文件结果
        """
        try:
            search_path = Path(path).resolve()

            # 检查路径是否存在
            if not search_path.exists():
                return {"error": f"路径不存在: {search_path}"}

            # 检查路径是否为目录
            if not search_path.is_dir():
                return {"error": f"路径不是目录: {search_path}"}

            # 查找文件
            files = []

            if recursive:
                # 递归搜索
                for root, _, filenames in os.walk(search_path):
                    for filename in filenames:
                        file_path = Path(root) / filename
                        files.append(file_path)
            else:
                # 仅搜索当前目录
                for filename in os.listdir(search_path):
                    file_path = search_path / filename
                    if file_path.is_file():
                        files.append(file_path)

            # 按大小分组
            size_groups = {}
            for file_path in files:
                try:
                    size = file_path.stat().st_size
                    if size not in size_groups:
                        size_groups[size] = []
                    size_groups[size].append(file_path)
                except Exception:
                    continue

            # 筛选可能重复的文件组
            duplicate_groups = {}
            for size, group in size_groups.items():
                if len(group) > 1:
                    # 如果只比较大小，直接添加到结果
                    if not compare_content:
                        duplicate_groups[size] = group
                    else:
                        # 比较内容
                        content_groups = {}
                        for file_path in group:
                            try:
                                # 计算文件哈希
                                file_hash = self._calculate_file_hash(file_path)
                                if file_hash not in content_groups:
                                    content_groups[file_hash] = []
                                content_groups[file_hash].append(file_path)
                            except Exception:
                                continue

                        # 只保留真正重复的文件组
                        for hash_val, hash_group in content_groups.items():
                            if len(hash_group) > 1:
                                if size not in duplicate_groups:
                                    duplicate_groups[size] = {}
                                duplicate_groups[size][hash_val] = hash_group

            # 格式化结果
            duplicates = []
            for size, hash_groups in duplicate_groups.items():
                for hash_val, group in hash_groups.items():
                    duplicates.append({
                        "size": size,
                        "size_str": self._format_size(size),
                        "count": len(group),
                        "files": [str(f) for f in group]
                    })

            logger.info(f"查找重复文件: 在 {search_path} 中找到 {len(duplicates)} 组重复文件")

            return {
                "success": True,
                "path": str(search_path),
                "recursive": recursive,
                "compare_content": compare_content,
                "total_files": len(files),
                "duplicate_groups": duplicates,
                "count": len(duplicates)
            }
        except Exception as e:
            error_msg = f"查找重复文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        计算文件哈希值

        参数:
            file_path: 文件路径

        返回:
            文件哈希值
        """
        import hashlib

        hash_func = hashlib.md5()

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)

        return hash_func.hexdigest()

    def _format_size(self, size: int) -> str:
        """
        格式化文件大小

        参数:
            size: 文件大小（字节）

        返回:
            格式化后的大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
