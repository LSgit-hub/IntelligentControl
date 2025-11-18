#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LM Studio本地模型接口实现模块
提供与LM Studio集成的本地模型接口实现
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional, Union

from src.ai_interface.base_ai import BaseAI
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LMStudio(BaseAI):
    """LM Studio本地模型接口实现"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化LM Studio本地模型接口

        参数:
            config: 配置信息
        """
        super().__init__(config)
        self.api_base = config.get("api_base", "http://localhost:1234")
        self.model = config.get("model", "default")

        # 检查服务是否可用
        self._check_service()

    def _get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self.list_models()

    def _get_provider_info(self) -> Dict[str, str]:
        """获取提供商信息"""
        return {
            "name": "LMStudio",
            "description": "本地LM Studio模型服务",
            "type": "local"
        }

    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """发送请求到LM Studio"""
        # 准备请求数据
        request_data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": kwargs.get("stream", False)
        }

        # 发送请求
        try:
            url = f"{self.api_base}/v1/chat/completions"
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=request_data, timeout=self.timeout)
            response.raise_for_status()

            response_data = response.json()

            # 提取内容
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

            return {
                "success": True,
                "content": content,
                "model": response_data.get("model", self.model),
                "provider": "LMStudio",
                "usage": response_data.get("usage", {"total_tokens": len(content.split())}),
                "response": content,
                "tokens_used": response_data.get("usage", {}).get("total_tokens", len(content.split())),
                "time_used": 0.0,
                "timestamp": time.time()
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"LM Studio请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理LM Studio响应失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _check_service(self) -> None:
        """
        检查LM Studio服务是否可用
        """
        try:
            # 检查服务健康状态
            models_url = f"{self.api_base}/v1/models"
            response = requests.get(models_url, timeout=5)

            if response.status_code == 200:
                logger.info(f"LM Studio服务可用: {self.api_base}")
            else:
                logger.warning(f"LM Studio服务状态异常: {response.status_code}")

        except Exception as e:
            logger.warning(f"无法连接到LM Studio服务: {str(e)}")

    def chat(self, message: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        与LM Studio模型进行对话

        参数:
            messages: 对话消息列表
            **kwargs: 其他参数

        返回:
            对话响应
        """
        # 准备消息
        messages = self._prepare_messages(message, system_prompt)

        # 准备请求数据
        request_data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "stream": False
        }

        # 发送请求
        try:
            url = f"{self.api_base}/v1/chat/completions"
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=request_data, timeout=self.timeout)
            response.raise_for_status()

            response_data = response.json()

            # 提取内容
            content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

            return {
                "success": True,
                "content": content,
                "model": response_data.get("model", self.model),
                "provider": "LMStudio",
                "usage": response_data.get("usage", {"total_tokens": len(content.split())}),
                "response": content,
                "tokens_used": response_data.get("usage", {}).get("total_tokens", len(content.split())),
                "time_used": 0.0,
                "timestamp": time.time()
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"LM Studio请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理LM Studio响应失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def list_models(self) -> List[str]:
        """
        获取LM Studio中可用的模型列表

        返回:
            模型列表
        """
        try:
            url = f"{self.api_base}/v1/models"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            models_data = response.json()
            models = []

            if "data" in models_data:
                models = [model["id"] for model in models_data["data"]]

            return models

        except Exception as e:
            logger.error(f"获取LM Studio模型列表失败: {str(e)}")
            return []

    def get_model_info(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取指定模型的信息

        参数:
            model_id: 模型ID，如果为None则使用当前模型

        返回:
            模型信息
        """
        try:
            if model_id is None:
                model_id = self.model

            url = f"{self.api_base}/v1/models/{model_id}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return {}
