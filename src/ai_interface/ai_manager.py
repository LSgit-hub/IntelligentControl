#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI管理器模块
管理多个AI服务提供商的接口
"""

import os
import json
from typing import Dict, Any, List, Optional

from src.ai_interface.base_ai import BaseAI
from src.ai_interface.openai import OpenAI
from src.ai_interface.local_model import LocalModel
from src.ai_interface.lmstudio import LMStudio
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class AIManager:
    """AI管理器类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化AI管理器

        参数:
            config: 配置信息
        """
        self.config = config
        self.current_provider = config.get("ai", {}).get("provider", "openai")
        self.current_model = config.get("ai", {}).get("model", "gpt-3.5-turbo")

        # 加载配置文件
        self.config_file = config.get("config_file", os.path.expanduser("~/.intelligent_control/ai_config.json"))
        self.load_config()

        # 初始化AI实例
        self.ai_instances = {}
        self._init_ai_instances()

        # 加载对话历史
        self.history_file = config.get("history_file", os.path.expanduser("~/.intelligent_control/ai_history.json"))
        self.conversation_history = {}
        self.load_history()

    def _init_ai_instances(self) -> None:
        """
        初始化AI实例
        """
        # 初始化OpenAI实例
        if "openai" in self.providers:
            openai_config = self.providers["openai"]
            self.ai_instances["openai"] = OpenAI(openai_config)

        # 初始化本地模型实例
        if "local" in self.providers:
            local_config = self.providers["local"]
            self.ai_instances["local"] = LocalModel(local_config)

        # 初始化LM Studio实例
        if "lmstudio" in self.providers:
            lmstudio_config = self.providers["lmstudio"]
            self.ai_instances["lmstudio"] = LMStudio(lmstudio_config)
        elif "lmstudio" in self.config:
            # 从主配置中获取LM Studio配置
            lmstudio_config = self.config["lmstudio"]
            self.ai_instances["lmstudio"] = LMStudio(lmstudio_config)

        logger.info(f"初始化AI实例完成: {list(self.ai_instances.keys())}")

    def load_config(self) -> None:
        """
        加载配置文件
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                    self.providers = config_data.get("providers", {})
                    self.current_provider = config_data.get("default_provider", "openai")
                    self.current_model = config_data.get("default_model", "gpt-3.5-turbo")

                    logger.info("配置文件加载成功")
            else:
                # 创建默认配置
                self.providers = {
                    "openai": {
                        "model": "gpt-3.5-turbo",
                        "api_key": "",
                        "api_base": "https://api.openai.com/v1",
                        "timeout": 30,
                        "max_tokens": 2000,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "cache_enabled": True,
                        "cache_dir": os.path.expanduser("~/.intelligent_control/cache"),
                        "cache_ttl": 3600
                    },
                    "local": {
                        "model": "llama-2-7b-chat",
                        "api_base": "http://localhost:8000",
                        "model_type": "llama",
                        "system_prompt": "你是一个智能助手",
                        "timeout": 30,
                        "max_tokens": 2000,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "cache_enabled": True,
                        "cache_dir": os.path.expanduser("~/.intelligent_control/cache"),
                        "cache_ttl": 3600
                    },
                    "lmstudio": {
                        "model": "default",
                        "api_base": "http://localhost:1234",
                        "timeout": 30,
                        "max_tokens": 2000,
                        "temperature": 0.7
                    }
                }

                self.current_provider = "openai"
                self.current_model = "gpt-3.5-turbo"

                # 保存默认配置
                self.save_config()

                logger.info("创建默认配置文件")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            # 使用默认配置
            self.providers = {
                "openai": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "",
                    "api_base": "https://api.openai.com/v1",
                    "timeout": 30,
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "cache_enabled": True,
                    "cache_dir": os.path.expanduser("~/.intelligent_control/cache"),
                    "cache_ttl": 3600
                }
            }
            self.current_provider = "openai"
            self.current_model = "gpt-3.5-turbo"

    def save_config(self) -> None:
        """
        保存配置文件
        """
        try:
            config_data = {
                "providers": self.providers,
                "default_provider": self.current_provider,
                "default_model": self.current_model
            }

            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            logger.info("配置文件保存成功")
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")

    def load_history(self) -> None:
        """
        加载对话历史
        """
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)

                logger.info("对话历史加载成功")
        except Exception as e:
            logger.error(f"加载对话历史失败: {str(e)}")
            self.conversation_history = {}

    def save_history(self) -> None:
        """
        保存对话历史
        """
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)

            logger.info("对话历史保存成功")
        except Exception as e:
            logger.error(f"保存对话历史失败: {str(e)}")

    def chat(self, message: str, provider: Optional[str] = None, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        发送对话请求

        参数:
            message: 用户消息
            provider: AI服务提供商
            model: 模型名称
            **kwargs: 其他参数

        返回:
            对话响应
        """
        # 确定使用哪个提供商
        if provider is None:
            provider = self.current_provider

        if provider not in self.ai_instances:
            return {
                "success": False,
                "error": f"不支持的AI服务提供商: {provider}"
            }

        # 确定使用哪个模型
        if model is None:
            model = self.current_model

        # 更新当前设置
        self.current_provider = provider
        self.current_model = model

        # 保存配置
        self.save_config()

        # 获取AI实例
        ai_instance = self.ai_instances[provider]

        # 发送对话请求
        result = ai_instance.chat(message, **kwargs)

        # 保存对话历史
        self._save_conversation(message, result, provider)

        return result

    def stream_chat(self, message: str, provider: Optional[str] = None, model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        发送流式对话请求

        参数:
            message: 用户消息
            provider: AI服务提供商
            model: 模型名称
            **kwargs: 其他参数

        返回:
            流式对话响应
        """
        # 确定使用哪个提供商
        if provider is None:
            provider = self.current_provider

        if provider not in self.ai_instances:
            return {
                "success": False,
                "error": f"不支持的AI服务提供商: {provider}"
            }

        if provider is None:
            return {
                "success": False,
                "error": "无法确定AI服务提供商"
            }

        if provider is None:
            return {
                "success": False,
                "error": "无法确定AI服务提供商"
            }

        # 确定使用哪个模型
        if model is None:
            model = self.current_model

        # 更新当前设置
        self.current_provider = provider
        self.current_model = model

        # 保存配置
        self.save_config()

        # 获取AI实例
        ai_instance = self.ai_instances[provider]

        # 发送流式对话请求
        result = ai_instance.stream_chat(message, **kwargs)

        # 保存对话历史
        self._save_conversation(message, result, provider)

        return result

    def get_models(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        获取可用模型列表

        参数:
            provider: AI服务提供商

        返回:
            模型列表
        """
        # 确定使用哪个提供商
        if provider is None:
            provider = self.current_provider

        if provider not in self.ai_instances:
            return {
                "success": False,
                "error": f"不支持的AI服务提供商: {provider}"
            }

        # 获取AI实例
        ai_instance = self.ai_instances[provider]

        # 获取模型列表
        return ai_instance.get_models()

    def get_providers(self) -> Dict[str, Any]:
        """
        获取所有AI服务提供商信息

        返回:
            提供商信息列表
        """
        providers_info = {}

        for provider_name, ai_instance in self.ai_instances.items():
            try:
                provider_info = ai_instance.get_provider_info()
                providers_info[provider_name] = provider_info
            except Exception as e:
                logger.error(f"获取提供商信息失败 {provider_name}: {str(e)}")
                providers_info[provider_name] = {
                    "name": provider_name,
                    "error": str(e)
                }

        return {
            "success": True,
            "providers": providers_info,
            "current": self.current_provider
        }

    def set_provider(self, provider: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        设置当前AI服务提供商

        参数:
            provider: AI服务提供商名称
            model: 模型名称

        返回:
            操作结果
        """
        if provider not in self.ai_instances:
            return {
                "success": False,
                "error": f"不支持的AI服务提供商: {provider}"
            }

        # 更新当前设置
        self.current_provider = provider
        if model:
            self.current_model = model

        # 保存配置
        self.save_config()

        logger.info(f"设置当前AI服务提供商: {provider}")
        return {
            "success": True,
            "message": f"已设置当前AI服务提供商: {provider}",
            "provider": provider,
            "model": self.current_model
        }

    def set_model(self, model: str) -> Dict[str, Any]:
        """
        设置当前模型

        参数:
            model: 模型名称

        返回:
            操作结果
        """
        # 更新当前设置
        self.current_model = model

        # 保存配置
        self.save_config()

        logger.info(f"设置当前模型: {model}")
        return {
            "success": True,
            "message": f"已设置当前模型: {model}",
            "model": model
        }

    def get_conversation_history(self, provider: Optional[str] = None, count: int = 10) -> Dict[str, Any]:
        """
        获取对话历史

        参数:
            provider: AI服务提供商
            count: 返回的历史记录数量

        返回:
            对话历史
        """
        if provider is None:
            provider = self.current_provider

        if provider not in self.conversation_history:
            self.conversation_history[provider] = []

        history = self.conversation_history[provider][-count:]

        return {
            "success": True,
            "provider": provider,
            "history": history,
            "count": len(history)
        }

    def clear_conversation_history(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        清除对话历史

        参数:
            provider: AI服务提供商

        返回:
            操作结果
        """
        if provider is None:
            provider = self.current_provider

        if provider in self.conversation_history:
            self.conversation_history[provider] = []

        # 保存历史
        self.save_history()

        logger.info(f"清除对话历史: {provider}")
        return {
            "success": True,
            "message": f"已清除对话历史: {provider}",
            "provider": provider
        }

    def _save_conversation(self, message: str, response: Dict[str, Any], provider: str) -> None:
        """
        保存对话记录

        参数:
            message: 用户消息
            response: AI响应
            provider: AI服务提供商
        """
        if provider not in self.conversation_history:
            self.conversation_history[provider] = []

        # 添加对话记录
        self.conversation_history[provider].append({
            "timestamp": response.get("timestamp", 0),
            "message": message,
            "response": response.get("response", ""),
            "provider": provider,
            "model": response.get("model", ""),
            "success": response.get("success", False),
            "error": response.get("error", "")
        })

        # 限制历史记录长度
        max_history = 100
        if len(self.conversation_history[provider]) > max_history:
            self.conversation_history[provider] = self.conversation_history[provider][-max_history:]

        # 保存历史
        self.save_history()

    def update_provider_config(self, provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新AI服务提供商配置

        参数:
            provider: AI服务提供商名称
            config: 新的配置

        返回:
            操作结果
        """
        if provider not in self.providers:
            return {
                "success": False,
                "error": f"不支持的AI服务提供商: {provider}"
            }

        # 更新配置
        self.providers[provider].update(config)

        # 重新初始化AI实例
        if provider in self.ai_instances:
            self.ai_instances[provider] = self._create_ai_instance(provider)

        # 保存配置
        self.save_config()

        logger.info(f"更新AI服务提供商配置: {provider}")
        return {
            "success": True,
            "message": f"已更新AI服务提供商配置: {provider}",
            "provider": provider
        }

    def _create_ai_instance(self, provider: str) -> BaseAI:
        """
        创建AI实例

        参数:
            provider: AI服务提供商名称

        返回:
            AI实例
        """
        config = self.providers[provider]

        if provider == "openai":
            return OpenAI(config)
        elif provider == "local":
            return LocalModel(config)
        else:
            raise ValueError(f"不支持的AI服务提供商: {provider}")
