#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地模型接口实现模块
提供本地运行的大语言模型接口实现
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional, Union

from .base_ai import BaseAI
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class LocalModel(BaseAI):
    """本地模型接口实现"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化本地模型接口

        参数:
            config: 配置信息
        """
        super().__init__(config)
        self.api_base = config.get("api_base", "http://localhost:8000")
        self.model_path = config.get("model_path", "")
        self.model_type = config.get("model_type", "llama")  # llama, qwen, chatglm等
        self.system_prompt = config.get("system_prompt", "你是一个智能助手")

        # 设置默认端点
        if not self.api_base:
            if self.model_type == "llama":
                self.api_base = "http://localhost:8000"
            elif self.model_type == "qwen":
                self.api_base = "http://localhost:8000"
            elif self.model_type == "chatglm":
                self.api_base = "http://localhost:8000"
            else:
                self.api_base = "http://localhost:8000"

        # 检查服务是否可用
        self._check_service()

    def _check_service(self) -> None:
        """
        检查本地服务是否可用
        """
        try:
            # 检查服务健康状态
            health_url = f"{self.api_base}/health"
            response = requests.get(health_url, timeout=5)

            if response.status_code == 200:
                logger.info(f"本地模型服务可用: {self.api_base}")
            else:
                logger.warning(f"本地模型服务状态异常: {response.status_code}")

        except Exception as e:
            logger.warning(f"无法连接到本地模型服务: {str(e)}")

    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送请求到本地模型API

        参数:
            messages: 对话消息列表
            **kwargs: 其他参数

        返回:
            响应数据
        """
        # 根据模型类型选择不同的端点
        if self.model_type in ["llama", "qwen"]:
            return self._make_llama_request(messages, **kwargs)
        elif self.model_type == "chatglm":
            return self._make_chatglm_request(messages, **kwargs)
        else:
            return self._make_generic_request(messages, **kwargs)

    def _make_llama_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送请求到Llama类型模型

        参数:
            messages: 对话消息列表
            **kwargs: 其他参数

        返回:
            响应数据
        """
        # 准备请求数据
        request_data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
            "stream": kwargs.get("stream", False),
            "stop": kwargs.get("stop", None)
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
            if request_data["stream"]:
                # 流式响应处理
                content = ""

                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8").replace("data: ", ""))

                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content += delta["content"]

                        except json.JSONDecodeError:
                            continue

                return {
                    "content": content,
                    "model": response_data.get("model", self.model),
                    "provider": "LocalModel",
                    "usage": {"total_tokens": len(content.split())}
                }
            else:
                # 非流式响应处理
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

                return {
                    "content": content,
                    "model": response_data.get("model", self.model),
                    "provider": "LocalModel",
                    "usage": {"total_tokens": len(content.split())}
                }

        except requests.exceptions.RequestException as e:
            error_msg = f"本地模型请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理本地模型响应失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _make_chatglm_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送请求到ChatGLM类型模型

        参数:
            messages: 对话消息列表
            **kwargs: 其他参数

        返回:
            响应数据
        """
        # 准备请求数据
        request_data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
            "stream": kwargs.get("stream", False)
        }

        # 发送请求
        try:
            url = f"{self.api_base}/chatglm"
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=request_data, timeout=self.timeout)
            response.raise_for_status()

            response_data = response.json()

            # 提取内容
            content = response_data.get("response", "")

            return {
                "content": content,
                "model": response_data.get("model", self.model),
                "provider": "LocalModel",
                "usage": {"total_tokens": len(content.split())}
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"ChatGLM模型请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理ChatGLM响应失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _make_generic_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送请求到通用本地模型

        参数:
            messages: 对话消息列表
            **kwargs: 其他参数

        返回:
            响应数据
        """
        # 准备请求数据
        request_data = {
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
            "stream": kwargs.get("stream", False)
        }

        # 发送请求
        try:
            url = f"{self.api_base}/generate"
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=request_data, timeout=self.timeout)
            response.raise_for_status()

            response_data = response.json()

            # 提取内容
            content = response_data.get("text", "")

            return {
                "content": content,
                "model": response_data.get("model", self.model),
                "provider": "LocalModel",
                "usage": {"total_tokens": len(content.split())}
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"本地模型请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理本地模型响应失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _get_available_models(self) -> List[str]:
        """
        获取可用的模型列表

        返回:
            模型列表
        """
        try:
            # 尝试获取模型列表
            if self.model_type in ["llama", "qwen"]:
                url = f"{self.api_base}/v1/models"
            elif self.model_type == "chatglm":
                url = f"{self.api_base}/models"
            else:
                url = f"{self.api_base}/models"

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            models_data = response.json()
            models = []

            if "data" in models_data:
                models = [model["id"] for model in models_data["data"]]
            elif "models" in models_data:
                models = [model["id"] for model in models_data["models"]]
            else:
                # 如果没有模型列表，使用配置中的模型
                models = [self.model]

            return models

        except Exception as e:
            logger.warning(f"获取本地模型列表失败: {str(e)}")
            # 返回配置中的模型
            return [self.model]

    def _get_provider_info(self) -> Dict[str, str]:
        """
        获取本地模型服务提供商信息

        返回:
            提供商信息
        """
        return {
            "name": "LocalModel",
            "description": f"本地运行的大语言模型 ({self.model_type})",
            "website": "",
            "api_docs": "",
            "api_base": self.api_base,
            "model_type": self.model_type
        }

    def load_model(self, model_path: str) -> Dict[str, Any]:
        """
        加载模型

        参数:
            model_path: 模型路径

        返回:
            操作结果
        """
        try:
            url = f"{self.api_base}/load_model"
            headers = {
                "Content-Type": "application/json"
            }

            request_data = {
                "model_path": model_path
            }

            response = requests.post(url, headers=headers, json=request_data, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            logger.info(f"模型加载成功: {model_path}")
            return {
                "success": True,
                "message": result.get("message", "模型加载成功")
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"模型加载失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"模型加载失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        返回:
            模型信息
        """
        try:
            url = f"{self.api_base}/model_info"
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            logger.info("获取模型信息成功")
            return {
                "success": True,
                "info": result
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"获取模型信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"获取模型信息失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def get_service_status(self) -> Dict[str, Any]:
        """
        获取服务状态

        返回:
            服务状态
        """
        try:
            url = f"{self.api_base}/status"
            headers = {
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            logger.info("获取服务状态成功")
            return {
                "success": True,
                "status": result
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"获取服务状态失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"获取服务状态失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
