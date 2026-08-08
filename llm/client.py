"""LLM Client - 统一封装大模型调用。

支持 OpenAI / DeepSeek / Qwen / vLLM。
禁止业务代码直接调用模型 SDK。
"""

import logging
from typing import Any, Optional

logger = logging.getLogger("poc2rule")


class LLMClient:
    """统一的大模型调用客户端。"""

    def __init__(self, llm_config: dict):
        self.config = llm_config
        self.provider = llm_config.get("provider", "openai")
        self.model = llm_config.get("model", "gpt-4o")
        self.temperature = llm_config.get("temperature", 0.1)
        self.max_tokens = llm_config.get("max_tokens", 4096)
        self.api_key = llm_config.get("api_key", "")
        self.base_url = llm_config.get("base_url", "")

        self._client = self._create_client()

    def _create_client(self):
        """根据 provider 创建对应的客户端。"""
        if self.provider == "openai":
            from openai import OpenAI
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            return OpenAI(**kwargs)

        elif self.provider in ("deepseek", "qwen", "vllm"):
            # DeepSeek / Qwen / vLLM 都兼容 OpenAI 接口
            from openai import OpenAI
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            else:
                # 默认 base_url
                defaults = {
                    "deepseek": "https://api.deepseek.com",
                    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                }
                kwargs["base_url"] = defaults.get(self.provider, "")
            return OpenAI(**kwargs)

        else:
            raise ValueError(f"不支持的 provider: {self.provider}")

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[dict] = None,
    ) -> str:
        """发送聊天请求，返回模型响应的文本内容。

        Args:
            messages: 消息列表，格式 [{"role": "...", "content": "..."}]
            temperature: 温度参数，默认使用配置值
            max_tokens: 最大 token 数，默认使用配置值
            response_format: 响应格式，如 {"type": "json_object"}

        Returns:
            模型响应的文本内容
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        logger.debug(f"LLM 调用: model={self.model}, provider={self.provider}")
        response = self._client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content
        logger.debug(f"LLM 响应: {content[:200]}...")
        return content

    def chat_json(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
    ) -> str:
        """发送聊天请求并强制返回 JSON 格式。"""
        return self.chat(
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
