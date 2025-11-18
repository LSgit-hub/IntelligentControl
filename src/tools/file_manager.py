#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件管理工具模块
提供文件和目录的高级管理功能
"""

import os
import shutil
import fnmatch
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class FileManager:
    """文件管理器类"""

    def __init__(self):
        """初始化文件管理器"""
        self.current_dir = os.getcwd()

    def copy_file(self, src: str, dst: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        复制文件或目录

        参数:
            src: 源文件或目录路径
            dst: 目标路径
            overwrite: 是否覆盖已存在的文件

        返回:
            操作结果
        """
        try:
            src_path = Path(src).resolve()
            dst_path = Path(dst).resolve()

            # 检查源是否存在
            if not src_path.exists():
                return {"error": f"源路径不存在: {src_path}"}

            # 检查目标是否已存在
            if dst_path.exists() and not overwrite:
                return {"error": f"目标路径已存在: {dst_path}"}

            # 创建目标目录（如果需要）
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # 执行复制
            if src_path.is_dir():
                shutil.copytree(src_path, dst_path, dirs_exist_ok=overwrite)
                logger.info(f"复制目录: {src_path} -> {dst_path}")
            else:
                shutil.copy2(src_path, dst_path)
                logger.info(f"复制文件: {src_path} -> {dst_path}")

            return {
                "success": True,
                "message": f"已复制: {src_path} -> {dst_path}",
                "source": str(src_path),
                "destination": str(dst_path)
            }
        except Exception as e:
            error_msg = f"复制失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def move_file(self, src: str, dst: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        移动文件或目录

        参数:
            src: 源文件或目录路径
            dst: 目标路径
            overwrite: 是否覆盖已存在的文件

        返回:
            操作结果
        """
        try:
            src_path = Path(src).resolve()
            dst_path = Path(dst).resolve()

            # 检查源是否存在
            if not src_path.exists():
                return {"error": f"源路径不存在: {src_path}"}

            # 检查目标是否已存在
            if dst_path.exists() and not overwrite:
                return {"error": f"目标路径已存在: {dst_path}"}

            # 创建目标目录（如果需要）
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # 执行移动
            shutil.move(str(src_path), str(dst_path))
            logger.info(f"移动: {src_path} -> {dst_path}")

            return {
                "success": True,
                "message": f"已移动: {src_path} -> {dst_path}",
                "source": str(src_path),
                "destination": str(dst_path)
            }
        except Exception as e:
            error_msg = f"移动失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def rename_file(self, path: str, new_name: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        重命名文件或目录

        参数:
            path: 文件或目录路径
            new_name: 新名称
            overwrite: 是否覆盖已存在的同名文件

        返回:
            操作结果
        """
        try:
            path_obj = Path(path).resolve()

            # 检查路径是否存在
            if not path_obj.exists():
                return {"error": f"路径不存在: {path_obj}"}

            # 构造新路径
            parent_dir = path_obj.parent
            new_path = parent_dir / new_name

            # 检查新路径是否已存在
            if new_path.exists() and not overwrite:
                return {"error": f"路径已存在: {new_path}"}

            # 执行重命名
            path_obj.rename(new_path)
            logger.info(f"重命名: {path_obj} -> {new_path}")

            return {
                "success": True,
                "message": f"已重命名: {path_obj} -> {new_path}",
                "old_path": str(path_obj),
                "new_path": str(new_path)
            }
        except Exception as e:
            error_msg = f"重命名失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def search_files(self, pattern: str, path: str = ".", recursive: bool = True) -> Dict[str, Any]:
        """
        搜索文件

        参数:
            pattern: 文件匹配模式（支持通配符）
            path: 搜索路径
            recursive: 是否递归搜索子目录

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
                        matches.append(str(file_path))
            else:
                # 仅搜索当前目录
                for file in fnmatch.listdir(search_path, pattern):
                    file_path = search_path / file
                    if file_path.is_file():
                        matches.append(str(file_path))

            logger.info(f"搜索文件: 在 {search_path} 中找到 {len(matches)} 个匹配项")

            return {
                "success": True,
                "pattern": pattern,
                "path": str(search_path),
                "recursive": recursive,
                "matches": matches,
                "count": len(matches)
            }
        except Exception as e:
            error_msg = f"搜索文件失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def calculate_file_hash(self, file_path: str, algorithm: str = "sha256") -> Dict[str, Any]:
        """
        计算文件哈希值

        参数:
            file_path: 文件路径
            algorithm: 哈希算法（md5, sha1, sha256等）

        返回:
            哈希值
        """
        try:
            path = Path(file_path).resolve()

            # 检查文件是否存在
            if not path.exists():
                return {"error": f"文件不存在: {path}"}

            # 检查是否为文件
            if not path.is_file():
                return {"error": f"路径不是文件: {path}"}

            # 计算哈希
            hash_func = hashlib.new(algorithm)

            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_func.update(chunk)

            file_hash = hash_func.hexdigest()

            logger.info(f"计算文件哈希: {path} ({algorithm})")

            return {
                "success": True,
                "file_path": str(path),
                "algorithm": algorithm,
                "hash": file_hash
            }
        except Exception as e:
            error_msg = f"计算文件哈希失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件详细信息

        参数:
            file_path: 文件路径

        返回:
            文件信息
        """
        try:
            path = Path(file_path).resolve()

            # 检查路径是否存在
            if not path.exists():
                return {"error": f"路径不存在: {path}"}

            # 获取文件信息
            stat = path.stat()

            info = {
                "path": str(path),
                "name": path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "accessed": stat.st_atime,
                "is_dir": path.is_dir(),
                "is_file": path.is_file(),
                "is_symlink": path.is_symlink(),
                "suffix": path.suffix,
                "stem": path.stem,
                "parent": str(path.parent)
            }

            # 格式化时间戳
            from datetime import datetime
            info["modified_str"] = datetime.fromtimestamp(info["modified"]).strftime("%Y-%m-%d %H:%M:%S")
            info["created_str"] = datetime.fromtimestamp(info["created"]).strftime("%Y-%m-%d %H:%M:%S")
            info["accessed_str"] = datetime.fromtimestamp(info["accessed"]).strftime("%Y-%m-%d %H:%M:%S")

            # 格式化文件大小
            info["size_str"] = self._format_size(info["size"])

            logger.info(f"获取文件信息: {path}")

            return {
                "success": True,
                "info": info
            }
        except Exception as e:
            error_msg = f"获取文件信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def compress_file(self, src_path: str, dst_path: str, format: str = "zip") -> Dict[str, Any]:
        """
        压缩文件或目录

        参数:
            src_path: 源文件或目录路径
            dst_path: 目标压缩文件路径
            format: 压缩格式（zip, tar, gz）

        返回:
            操作结果
        """
        try:
            src = Path(src_path).resolve()
            dst = Path(dst_path).resolve()

            # 检查源是否存在
            if not src.exists():
                return {"error": f"源路径不存在: {src}"}

            # 创建目标目录（如果需要）
            dst.parent.mkdir(parents=True, exist_ok=True)

            # 执行压缩
            if format.lower() == "zip":
                import zipfile

                with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    if src.is_dir():
                        for root, _, files in os.walk(src):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(src)
                                zipf.write(file_path, arcname)
                    else:
                        zipf.write(src, src.name)
            elif format.lower() in ["tar", "gz"]:
                import tarfile

                mode = "w:gz" if format.lower() == "gz" else "w"
                with tarfile.open(dst, mode) as tar:
                    tar.add(src, arcname=src.name)
            else:
                return {"error": f"不支持的压缩格式: {format}"}

            logger.info(f"压缩: {src} -> {dst} ({format})")

            return {
                "success": True,
                "message": f"已压缩: {src} -> {dst}",
                "source": str(src),
                "destination": str(dst),
                "format": format
            }
        except Exception as e:
            error_msg = f"压缩失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def extract_file(self, src_path: str, dst_path: str = None) -> Dict[str, Any]:
        """
        解压文件

        参数:
            src_path: 源压缩文件路径
            dst_path: 目标解压目录路径，如果为None则解压到当前目录

        返回:
            操作结果
        """
        try:
            src = Path(src_path).resolve()

            # 检查源是否存在
            if not src.exists():
                return {"error": f"源路径不存在: {src}"}

            # 确定目标路径
            if dst_path is None:
                dst = src.parent / src.stem
            else:
                dst = Path(dst_path).resolve()

            # 创建目标目录（如果需要）
            dst.mkdir(parents=True, exist_ok=True)

            # 根据文件扩展名确定解压方式
            if src.suffix.lower() == ".zip":
                import zipfile

                with zipfile.ZipFile(src, 'r') as zipf:
                    zipf.extractall(dst)
            elif src.suffix.lower() == ".tar" or src.name.endswith(".tar.gz") or src.name.endswith(".tgz"):
                import tarfile

                with tarfile.open(src, 'r:*') as tar:
                    tar.extractall(dst)
            else:
                return {"error": f"不支持的压缩格式: {src.suffix}"}

            logger.info(f"解压: {src} -> {dst}")

            return {
                "success": True,
                "message": f"已解压: {src} -> {dst}",
                "source": str(src),
                "destination": str(dst)
            }
        except Exception as e:
            error_msg = f"解压失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

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
