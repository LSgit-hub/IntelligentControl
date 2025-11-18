#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Windows注册表访问工具模块
提供注册表读取和修改功能
"""

import os
import sys
import winreg
from typing import Dict, Any, List, Optional, Union

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RegistryManager:
    """注册表管理器类"""

    def __init__(self):
        """初始化注册表管理器"""
        self.hives = {
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CURRENT_CONFIG": winreg.HKEY_CURRENT_CONFIG
        }

    def list_hives(self) -> Dict[str, Any]:
        """
        列出所有注册表根项

        返回:
            注册表根项列表
        """
        try:
            hives = []

            for name, handle in self.hives.items():
                hive_info = {
                    "name": name,
                    "handle": handle,
                    "description": self._get_hive_description(handle)
                }
                hives.append(hive_info)

            logger.info("列出注册表根项成功")
            return {
                "success": True,
                "hives": hives
            }
        except Exception as e:
            error_msg = f"列出注册表根项失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def list_keys(self, path: str) -> Dict[str, Any]:
        """
        列出指定注册表项下的所有子项

        参数:
            path: 注册表项路径

        返回:
            子项列表
        """
        try:
            # 解析路径
            hive_name, sub_path = self._parse_path(path)
            if not hive_name:
                return {"error": "无效的注册表路径"}

            hive = self.hives[hive_name]

            # 打开注册表项
            key = winreg.OpenKey(hive, sub_path)

            # 枚举子项
            sub_keys = []
            i = 0
            while True:
                try:
                    sub_key_name = winreg.EnumKey(key, i)
                    sub_key_info = {
                        "name": sub_key_name,
                        "path": f"{path}\{sub_key_name}"
                    }
                    sub_keys.append(sub_key_info)
                    i += 1
                except WindowsError:
                    break

            # 关闭键
            winreg.CloseKey(key)

            logger.info(f"列出注册表子项成功: {path}")
            return {
                "success": True,
                "path": path,
                "sub_keys": sub_keys,
                "count": len(sub_keys)
            }
        except WindowsError as e:
            error_msg = f"无法访问注册表项: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"列出注册表子项失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def list_values(self, path: str) -> Dict[str, Any]:
        """
        列出指定注册表项下的所有值

        参数:
            path: 注册表项路径

        返回:
            值列表
        """
        try:
            # 解析路径
            hive_name, sub_path = self._parse_path(path)
            if not hive_name:
                return {"error": "无效的注册表路径"}

            hive = self.hives[hive_name]

            # 打开注册表项
            key = winreg.OpenKey(hive, sub_path)

            # 枚举值
            values = []

            # 获取默认值
            try:
                default_value, value_type = winreg.QueryValueEx(key, None)
                value_info = {
                    "name": "(默认)",
                    "type": self._get_value_type_name(value_type),
                    "data": self._format_value_data(default_value, value_type)
                }
                values.append(value_info)
            except WindowsError:
                pass

            # 获取其他值
            i = 0
            while True:
                try:
                    value_name, value_type, value_data = winreg.EnumValue(key, i)
                    value_info = {
                        "name": value_name,
                        "type": self._get_value_type_name(value_type),
                        "data": self._format_value_data(value_data, value_type)
                    }
                    values.append(value_info)
                    i += 1
                except WindowsError:
                    break

            # 关闭键
            winreg.CloseKey(key)

            logger.info(f"列出注册表值成功: {path}")
            return {
                "success": True,
                "path": path,
                "values": values,
                "count": len(values)
            }
        except WindowsError as e:
            error_msg = f"无法访问注册表项: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"列出注册表值失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_value(self, path: str, value_name: str) -> Dict[str, Any]:
        """
        获取指定注册表项的值

        参数:
            path: 注册表项路径
            value_name: 值名称

        返回:
            值信息
        """
        try:
            # 解析路径
            hive_name, sub_path = self._parse_path(path)
            if not hive_name:
                return {"error": "无效的注册表路径"}

            hive = self.hives[hive_name]

            # 打开注册表项
            key = winreg.OpenKey(hive, sub_path)

            # 获取值
            value_data, value_type = winreg.QueryValueEx(key, value_name)

            # 关闭键
            winreg.CloseKey(key)

            value_info = {
                "path": path,
                "name": value_name,
                "type": self._get_value_type_name(value_type),
                "data": self._format_value_data(value_data, value_type)
            }

            logger.info(f"获取注册表值成功: {path}\{value_name}")
            return {
                "success": True,
                "value": value_info
            }
        except WindowsError as e:
            error_msg = f"无法访问注册表项或值: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"获取注册表值失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def set_value(self, path: str, value_name: str, value_data: Any, value_type: str = "REG_SZ") -> Dict[str, Any]:
        """
        设置指定注册表项的值

        参数:
            path: 注册表项路径
            value_name: 值名称
            value_data: 值数据
            value_type: 值类型

        返回:
            操作结果
        """
        try:
            # 解析路径
            hive_name, sub_path = self._parse_path(path)
            if not hive_name:
                return {"error": "无效的注册表路径"}

            hive = self.hives[hive_name]

            # 转换值类型
            reg_type = self._get_value_type(value_type)
            if reg_type is None:
                return {"error": f"不支持的注册表值类型: {value_type}"}

            # 打开注册表项
            key = winreg.OpenKey(hive, sub_path, 0, winreg.KEY_SET_VALUE)

            # 设置值
            winreg.SetValueEx(key, value_name, 0, reg_type, value_data)

            # 关闭键
            winreg.CloseKey(key)

            logger.info(f"设置注册表值成功: {path}\{value_name} = {value_data}")
            return {
                "success": True,
                "message": f"已设置注册表值: {path}\{value_name} = {value_data}"
            }
        except WindowsError as e:
            error_msg = f"无法访问注册表项或值: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"设置注册表值失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def create_key(self, path: str) -> Dict[str, Any]:
        """
        创建注册表项

        参数:
            path: 注册表项路径

        返回:
            操作结果
        """
        try:
            # 解析路径
            hive_name, sub_path = self._parse_path(path)
            if not hive_name:
                return {"error": "无效的注册表路径"}

            hive = self.hives[hive_name]

            # 创建注册表项
            key = winreg.CreateKey(hive, sub_path)

            # 关闭键
            winreg.CloseKey(key)

            logger.info(f"创建注册表项成功: {path}")
            return {
                "success": True,
                "message": f"已创建注册表项: {path}"
            }
        except WindowsError as e:
            error_msg = f"无法创建注册表项: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"创建注册表项失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def delete_key(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        删除注册表项

        参数:
            path: 注册表项路径
            recursive: 是否递归删除子项

        返回:
            操作结果
        """
        try:
            # 解析路径
            hive_name, sub_path = self._parse_path(path)
            if not hive_name:
                return {"error": "无效的注册表路径"}

            hive = self.hives[hive_name]

            # 删除注册表项
            if recursive:
                winreg.DeleteKey(hive, sub_path)
            else:
                winreg.DeleteKeyEx(hive, sub_path)

            logger.info(f"删除注册表项成功: {path}")
            return {
                "success": True,
                "message": f"已删除注册表项: {path}"
            }
        except WindowsError as e:
            error_msg = f"无法删除注册表项: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"删除注册表项失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def delete_value(self, path: str, value_name: str) -> Dict[str, Any]:
        """
        删除注册表值

        参数:
            path: 注册表项路径
            value_name: 值名称

        返回:
            操作结果
        """
        try:
            # 解析路径
            hive_name, sub_path = self._parse_path(path)
            if not hive_name:
                return {"error": "无效的注册表路径"}

            hive = self.hives[hive_name]

            # 打开注册表项
            key = winreg.OpenKey(hive, sub_path, 0, winreg.KEY_SET_VALUE)

            # 删除值
            winreg.DeleteValue(key, value_name)

            # 关闭键
            winreg.CloseKey(key)

            logger.info(f"删除注册表值成功: {path}\{value_name}")
            return {
                "success": True,
                "message": f"已删除注册表值: {path}\{value_name}"
            }
        except WindowsError as e:
            error_msg = f"无法删除注册表值: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"删除注册表值失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def _parse_path(self, path: str) -> tuple:
        """
        解析注册表路径

        参数:
            path: 注册表路径

        返回:
            (根项名称, 子路径)
        """
        # 分割路径
        parts = path.split("\\", 1)

        if len(parts) < 2:
            return None, ""

        hive_name = parts[0]
        sub_path = parts[1] if parts[1] else ""

        return hive_name, sub_path

    def _get_hive_description(self, hive: int) -> str:
        """
        获取注册表根项描述

        参数:
            hive: 注册表根项句柄

        返回:
            描述字符串
        """
        descriptions = {
            winreg.HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT - 存储文件关联和COM对象信息",
            winreg.HKEY_CURRENT_USER: "HKEY_CURRENT_USER - 存储当前用户配置信息",
            winreg.HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE - 存储计算机配置信息",
            winreg.HKEY_USERS: "HKEY_USERS - 存储所有用户配置信息",
            winreg.HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG - 存储当前硬件配置信息"
        }

        return descriptions.get(hive, "未知根项")

    def _get_value_type_name(self, value_type: int) -> str:
        """
        获取注册表值类型名称

        参数:
            value_type: 值类型

        返回:
            类型名称
        """
        type_names = {
            winreg.REG_SZ: "REG_SZ (字符串)",
            winreg.REG_EXPAND_SZ: "REG_EXPAND_SZ (可扩展字符串)",
            winreg.REG_BINARY: "REG_BINARY (二进制)",
            winreg.REG_DWORD: "REG_DWORD (32位整数)",
            winreg.REG_QWORD: "REG_QWORD (64位整数)",
            winreg.REG_MULTI_SZ: "REG_MULTI_SZ (多字符串)",
            winreg.REG_RESOURCE_LIST: "REG_RESOURCE_LIST (资源列表)",
            winreg.REG_FULL_RESOURCE_DESCRIPTOR: "REG_FULL_RESOURCE_DESCRIPTOR (完整资源描述符)",
            winreg.REG_RESOURCE_REQUIREMENTS_LIST: "REG_RESOURCE_REQUIREMENTS_LIST (资源需求列表)"
        }

        return type_names.get(value_type, "未知类型")

    def _get_value_type(self, type_name: str) -> Optional[int]:
        """
        获取注册表值类型

        参数:
            type_name: 类型名称

        返回:
            值类型
        """
        type_mapping = {
            "REG_SZ": winreg.REG_SZ,
            "REG_EXPAND_SZ": winreg.REG_EXPAND_SZ,
            "REG_BINARY": winreg.REG_BINARY,
            "REG_DWORD": winreg.REG_DWORD,
            "REG_QWORD": winreg.REG_QWORD,
            "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
            "REG_RESOURCE_LIST": winreg.REG_RESOURCE_LIST,
            "REG_FULL_RESOURCE_DESCRIPTOR": winreg.REG_FULL_RESOURCE_DESCRIPTOR,
            "REG_RESOURCE_REQUIREMENTS_LIST": winreg.REG_RESOURCE_REQUIREMENTS_LIST
        }

        return type_mapping.get(type_name.upper())

    def _format_value_data(self, value_data: Any, value_type: int) -> str:
        """
        格式化值数据

        参数:
            value_data: 值数据
            value_type: 值类型

        返回:
            格式化后的数据
        """
        try:
            if value_type == winreg.REG_SZ or value_type == winreg.REG_EXPAND_SZ:
                return str(value_data)
            elif value_type == winreg.REG_BINARY:
                return " ".join(f"{b:02X}" for b in value_data)
            elif value_type == winreg.REG_DWORD:
                return str(value_data)
            elif value_type == winreg.REG_QWORD:
                return str(value_data)
            elif value_type == winreg.REG_MULTI_SZ:
                return ", ".join(value_data)
            else:
                return str(value_data)
        except Exception:
            return str(value_data)
