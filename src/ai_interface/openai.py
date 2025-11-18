#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OpenAI接口实现模块
提供OpenAI API的接口实现
"""

import os
import json
import time
import requests
from typing import Dict, Any, List, Optional, Union

from .base_ai import BaseAI
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class OpenAI(BaseAI):
    """OpenAI接口实现"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化OpenAI接口

        参数:
            config: 配置信息
        """
        super().__init__(config)
        self.api_version = config.get("api_version", "2023-12-01")
        self.organization = config.get("organization", "")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if self.organization:
            self.headers["OpenAI-Organization"] = self.organization

        # 端点URL
        self.endpoint_url = config.get("endpoint_url", "https://api.openai.com/v1/chat/completions")

    def _make_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        发送请求到OpenAI API

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
            "frequency_penalty": kwargs.get("frequency_penalty", self.frequency_penalty),
            "presence_penalty": kwargs.get("presence_penalty", self.presence_penalty),
            "stream": kwargs.get("stream", False)
        }

        # 添加流式处理参数
        if request_data["stream"]:
            request_data["stream_options"] = {"include_usage": True}

        # 发送请求
        try:
            response = requests.post(
                self.endpoint_url,
                headers=self.headers,
                json=request_data,
                timeout=self.timeout
            )

            response.raise_for_status()

            # 处理响应
            response_data = response.json()

            # 提取内容
            if request_data["stream"]:
                # 流式响应处理
                content = ""
                usage = None

                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8").replace("data: ", ""))

                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content += delta["content"]

                            if "usage" in chunk:
                                usage = chunk["usage"]

                        except json.JSONDecodeError:
                            continue

                return {
                    "content": content,
                    "model": response_data.get("model", self.model),
                    "provider": "OpenAI",
                    "usage": usage
                }
            else:
                # 非流式响应处理
                content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

                return {
                    "content": content,
                    "model": response_data.get("model", self.model),
                    "provider": "OpenAI",
                    "usage": response_data.get("usage", {})
                }

        except requests.exceptions.RequestException as e:
            error_msg = f"OpenAI API请求失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理OpenAI响应失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _get_available_models(self) -> List[str]:
        """
        获取可用的模型列表

        返回:
            模型列表
        """
        try:
            url = "https://api.openai.com/v1/models"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            models_data = response.json()
            models = [model["id"] for model in models_data.get("data", [])]

            return models

        except requests.exceptions.RequestException as e:
            error_msg = f"获取OpenAI模型列表失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"处理OpenAI模型列表失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def _get_provider_info(self) -> Dict[str, str]:
        """
        获取OpenAI服务提供商信息

        返回:
            提供商信息
        """
        return {
            "name": "OpenAI",
            "description": "OpenAI API接口",
            "website": "https://openai.com",
            "api_docs": "https://platform.openai.com/docs/api-reference/chat"
        }

    def create_image(self, prompt: str, size: str = "1024x1024", n: int = 1) -> Dict[str, Any]:
        """
        创建图像

        参数:
            prompt: 图像描述
            size: 图像尺寸
            n: 生成图像数量

        返回:
            图像生成结果
        """
        try:
            url = "https://api.openai.com/v1/images/generations"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            request_data = {
                "prompt": prompt,
                "n": n,
                "size": size
            }

            response = requests.post(url, headers=headers, json=request_data, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()

            logger.info(f"图像生成成功: {n} 张图像")
            return {
                "success": True,
                "images": result.get("data", []),
                "count": n
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"图像生成失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"图像生成失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def create_audio(self, text: str, voice: str = "alloy", format: str = "mp3") -> Dict[str, Any]:
        """
        创建音频

        参数:
            text: 要转换的文本
            voice: 语音类型
            format: 音频格式

        返回:
            音频生成结果
        """
        try:
            url = "https://api.openai.com/v1/audio/speech"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            request_data = {
                "model": "tts-1",
                "input": text,
                "voice": voice,
                "response_format": format
            }

            response = requests.post(url, headers=headers, json=request_data, timeout=self.timeout)
            response.raise_for_status()

            # 返回音频数据
            audio_data = response.content

            logger.info(f"音频生成成功: {len(audio_data)} 字节")
            return {
                "success": True,
                "audio_data": audio_data,
                "format": format,
                "size": len(audio_data)
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"音频生成失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"音频生成失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """
        转录音频

        参数:
            audio_file: 音频文件路径

        返回:
            转录结果
        """
        try:
            url = "https://api.openai.com/v1/audio/transcriptions"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            with open(audio_file, "rb") as f:
                files = {
                    "file": f,
                    "model": (None, "whisper-1")
                }

                response = requests.post(url, headers=headers, files=files, timeout=self.timeout)
                response.raise_for_status()

            result = response.json()

            logger.info(f"音频转录成功: {result.get('text', '')}")
            return {
                "success": True,
                "text": result.get("text", ""),
                "language": result.get("language", "")
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"音频转录失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"音频转录失败: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
