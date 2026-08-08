"""PluginManager - 插件管理器。

动态加载和管理所有规则格式插件。
新增规则格式时 Workflow 不需要修改。
"""

import importlib
import logging
from pathlib import Path
from typing import Optional

from plugins.base import PluginBase

logger = logging.getLogger("poc2rule")


class PluginManager:
    """插件管理器。

    负责：
    - 加载已启用的插件
    - 提供插件查询接口
    - 列出可用的插件
    """

    def __init__(self, plugin_config: dict):
        self.config = plugin_config
        self._plugins: dict[str, PluginBase] = {}
        self._load_plugins()

    def _load_plugins(self) -> None:
        """加载配置中启用的插件。"""
        enabled = self.config.get("enabled", ["snort"])

        for plugin_name in enabled:
            try:
                plugin = self._load_plugin(plugin_name)
                if plugin:
                    self._plugins[plugin.name] = plugin
                    logger.info(f"插件已加载: {plugin.name}")
            except Exception as e:
                logger.error(f"加载插件失败 [{plugin_name}]: {e}")

    def _load_plugin(self, name: str) -> Optional[PluginBase]:
        """动态加载单个插件模块。"""
        try:
            module = importlib.import_module(f"plugins.{name}.plugin")
            plugin_cls = getattr(module, "Plugin", None)
            if plugin_cls is None:
                logger.warning(f"插件 {name} 没有 Plugin 类")
                return None

            plugin_config = self.config.get(name, {})
            return plugin_cls(plugin_config)
        except ImportError as e:
            logger.warning(f"插件模块导入失败 [{name}]: {e}")
            return None

    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """获取指定名称的插件。"""
        return self._plugins.get(name)

    def list_plugins(self) -> list[str]:
        """列出所有已加载的插件名称。"""
        return list(self._plugins.keys())

    def get_schema(self, name: str) -> dict:
        """获取指定插件的规则 schema。"""
        plugin = self._plugins.get(name)
        if plugin:
            return plugin.get_schema()
        return {}

    def get_examples(self, name: str) -> list[str]:
        """获取指定插件的示例规则。"""
        plugin = self._plugins.get(name)
        if plugin:
            return plugin.get_examples()
        return []
