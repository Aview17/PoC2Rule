"""AppContext - 全局应用上下文。

管理配置、LLM 客户端、插件管理器等全局资源。
"""

import os
from pathlib import Path
from typing import Any

import yaml


class AppContext:
    """全局应用上下文，持有配置和全局资源引用。"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self._llm_client = None
        self._plugin_manager = None
        self._inference_service = None
        self._prompt_builder = None

    # ------------------------------------------------------------------
    # 配置加载
    # ------------------------------------------------------------------

    def _load_config(self, config_path: str) -> dict:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}

        return self._resolve_env_vars(raw)

    def _resolve_env_vars(self, data: Any) -> Any:
        """递归解析配置中的环境变量引用 ${VAR_NAME}。"""
        if isinstance(data, dict):
            return {k: self._resolve_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._resolve_env_vars(i) for i in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            var_name = data[2:-1]
            return os.environ.get(var_name, "")
        return data

    # ------------------------------------------------------------------
    # 懒加载属性
    # ------------------------------------------------------------------

    @property
    def llm_client(self):
        """LLM 客户端 (懒加载)。"""
        if self._llm_client is None:
            from llm.client import LLMClient
            self._llm_client = LLMClient(self.config.get("llm", {}))
        return self._llm_client

    @property
    def plugin_manager(self):
        """插件管理器 (懒加载)。"""
        if self._plugin_manager is None:
            from plugins.manager import PluginManager
            self._plugin_manager = PluginManager(self.config.get("plugins", {}))
        return self._plugin_manager

    @property
    def inference_service(self):
        """推理服务 (懒加载)。"""
        if self._inference_service is None:
            from llm.inference import InferenceService
            self._inference_service = InferenceService(self)
        return self._inference_service

    @property
    def prompt_builder(self):
        """Prompt 构建器 (懒加载)。"""
        if self._prompt_builder is None:
            from llm.prompt_builder import PromptBuilder
            self._prompt_builder = PromptBuilder()
        return self._prompt_builder

    def get_workspace_dir(self) -> str:
        """获取工作目录路径。"""
        ws = self.config.get("workspace", {})
        return ws.get("base_dir", "./workspace")
