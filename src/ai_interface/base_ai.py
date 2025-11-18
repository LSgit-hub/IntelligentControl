#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI接口基类模块
定义AI接口的通用接口和功能
"""

import os
import json
import time
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseAI(ABC):
    """AI接口基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI接口

        参数:
            config: 配置信息
        """
        self.config = config
        self.model = config.get("model", "default")
        self.api_key = config.get("api_key", "")
        self.api_base = config.get("api_base", "")
        self.timeout = config.get("timeout", 30)
        self.max_tokens = config.get("max_tokens", 2000)
        self.temperature = config.get("temperature", 0.7)
        self.top_p = config.get("top_p", 0.9)
        self.frequency_penalty = config.get("frequency_penalty", 0)
        self.presence_penalty = config.get("presence_penalty", 0)

        # 对话历史
        self.conversation_history = []
        self.max_history = config.get("max_history", 10)

        # 缓存
        self.cache_enabled = config.get("cache_enabled", True)
        self.cache_dir = config.get("cache_dir", os.path.expanduser("~/.intelligent_control/cache"))
        self.cache_ttl = config.get("cache_ttl", 3600)  # 1小时

        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)

    @abstractmethod
    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送请求到AI服务

        参数:
            messages: 对话消息列表
            **kwargs: 其他参数

        返回:
            响应数据
        """
        pass

    @abstractmethod
    def _get_available_models(self) -> List[str]:
        """
        获取可用的模型列表

        返回:
            模型列表
        """
        pass

    @abstractmethod
    def _get_provider_info(self) -> Dict[str, str]:
        """
        获取AI服务提供商信息

        返回:
            提供商信息
        """
        pass

    def chat(self, message: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        发送对话请求

        参数:
            message: 用户消息
            system_prompt: 系统提示词
            **kwargs: 其他参数

        返回:
            对话响应
        """
        # 检查缓存
        if self.cache_enabled:
            cache_key = self._generate_cache_key(message, system_prompt)
            cached_response = self._get_from_cache(cache_key)
            if cached_response:
                logger.info(f"使用缓存响应: {cache_key}")
                return cached_response

        # 准备消息
        messages = self._prepare_messages(message, system_prompt)

        # 发送请求
        try:
            start_time = time.time()
            response = self._make_request(messages, **kwargs)
            end_time = time.time()

            # 记录对话历史
            self._add_to_history(message, response)

            # 计算token使用情况（如果支持）
            tokens_used = response.get("usage", {}).get("total_tokens", 0)

            result = {
                "success": True,
                "response": response.get("content", ""),
                "model": response.get("model", self.model),
                "provider": response.get("provider", self._get_provider_info().get("name", "")),
                "tokens_used": tokens_used,
                "time_used": end_time - start_time,
                "timestamp": end_time
            }

            # 缓存响应
            if self.cache_enabled:
                self._save_to_cache(cache_key, result)

            logger.info(f"对话请求成功: {result['provider']} - {result['model']} - {tokens_used} tokens")
            return result

        except Exception as e:
            error_msg = f"对话请求失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": time.time()
            }

    def stream_chat(self, message: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        发送流式对话请求

        参数:
            message: 用户消息
            system_prompt: 系统提示词
            **kwargs: 其他参数

        返回:
            流式对话响应
        """
        # 准备消息
        messages = self._prepare_messages(message, system_prompt)

        # 发送流式请求
        try:
            start_time = time.time()
            response = self._make_request(messages, stream=True, **kwargs)
            end_time = time.time()

            # 记录对话历史
            self._add_to_history(message, response)

            result = {
                "success": True,
                "response": response.get("content", ""),
                "model": response.get("model", self.model),
                "provider": response.get("provider", self._get_provider_info().get("name", "")),
                "time_used": end_time - start_time,
                "timestamp": end_time,
                "stream": True
            }

            logger.info(f"流式对话请求成功: {result['provider']} - {result['model']}")
            return result

        except Exception as e:
            error_msg = f"流式对话请求失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": time.time()
            }

    def get_models(self) -> Dict[str, Any]:
        """
        获取可用模型列表

        返回:
            模型列表
        """
        try:
            models = self._get_available_models()

            logger.info(f"获取模型列表成功: {len(models)} 个模型")
            return {
                "success": True,
                "models": models,
                "count": len(models),
                "provider": self._get_provider_info().get("name", "")
            }
        except Exception as e:
            error_msg = f"获取模型列表失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def get_provider_info(self) -> Dict[str, Any]:
        """
        获取AI服务提供商信息

        返回:
            提供商信息
        """
        try:
            info = self._get_provider_info()

            logger.info("获取提供商信息成功")
            return {
                "success": True,
                "provider": info
            }
        except Exception as e:
            error_msg = f"获取提供商信息失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

    def clear_history(self) -> Dict[str, Any]:
        """
        清除对话历史

        返回:
            操作结果
        """
        self.conversation_history = []

        logger.info("清除对话历史成功")
        return {
            "success": True,
            "message": "对话历史已清除"
        }

    def get_history(self, count: int = 10) -> Dict[str, Any]:
        """
        获取对话历史

        参数:
            count: 返回的历史记录数量

        返回:
            对话历史
        """
        history = self.conversation_history[-count:]

        logger.info(f"获取对话历史成功: {len(history)} 条记录")
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }

    def _prepare_messages(self, message: str, system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """
        准备对话消息

        参数:
            message: 用户消息
            system_prompt: 系统提示词

        返回:
            消息列表
        """
        messages = []

        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加历史对话
        for msg in self.conversation_history[-self.max_history:]:
            messages.append(msg)

        # 添加用户消息
        messages.append({"role": "user", "content": message})

        return messages

    def _add_to_history(self, message: str, response: Dict[str, Any]) -> None:
        """
        添加对话到历史记录

        参数:
            message: 用户消息
            response: AI响应
        """
        # 添加用户消息
        self.conversation_history.append({"role": "user", "content": message})

        # 添加AI响应
        if response.get("success"):
            self.conversation_history.append({
                "role": "assistant", 
                "content": response.get("response", "")
            })
        else:
            self.conversation_history.append({
                "role": "assistant", 
                "content": f"错误: {response.get('error', '')}"
            })

        # 限制历史记录长度
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]

    def _generate_cache_key(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        生成缓存键

        参数:
            message: 用户消息
            system_prompt: 系统提示词

        返回:
            缓存键
        """
        key_data = f"{message}_{system_prompt}_{self.model}_{self.temperature}_{self.top_p}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取数据

        参数:
            cache_key: 缓存键

        返回:
            缓存数据，如果不存在则返回None
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

            if not os.path.exists(cache_file):
                return None

            # 检查缓存是否过期
            file_time = os.path.getmtime(cache_file)
            if time.time() - file_time > self.cache_ttl:
                return None

            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            logger.warning(f"读取缓存失败: {str(e)}")
            return None

    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """
        保存数据到缓存

        参数:
            cache_key: 缓存键
            data: 要缓存的数据
        """
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

            # 只缓存成功的响应
            if data.get("success"):
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.warning(f"保存缓存失败: {str(e)}")

    def set_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新配置

        参数:
            config: 新的配置

        返回:
            操作结果
        """
        try:
            self.config.update(config)

            # 更新相关属性
            self.model = config.get("model", self.model)
            self.api_key = config.get("api_key", self.api_key)
            self.api_base = config.get("api_base", self.api_base)
            self.timeout = config.get("timeout", self.timeout)
            self.max_tokens = config.get("max_tokens", self.max_tokens)
            self.temperature = config.get("temperature", self.temperature)
            self.top_p = config.get("top_p", self.top_p)
            self.frequency_penalty = config.get("frequency_penalty", self.frequency_penalty)
            self.presence_penalty = config.get("presence_penalty", self.presence_penalty)
            self.max_history = config.get("max_history", self.max_history)

            logger.info("配置更新成功")
            return {
                "success": True,
                "message": "配置已更新"
            }
        except Exception as e:
            error_msg = f"配置更新失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
