"""PluginBase - 规则插件基类。

每个 Plugin 负责：
- Renderer（渲染规则）
- Validator（验证规则）
- Tester（测试规则）
- Schema（规则格式定义）
- Examples（示例规则）
"""

from abc import ABC, abstractmethod
from typing import Any


class PluginBase(ABC):
    """规则插件基类。

    新增规则格式时只需实现此接口，Workflow 不需要修改。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称，如 'snort'、'suricata'。"""
        ...

    @abstractmethod
    def render(self, detection_ir: Any, ctx: Any) -> str:
        """将 Detection IR 渲染为规则文本。

        Args:
            detection_ir: 中间检测规则 IR
            ctx: 应用上下文

        Returns:
            规则文本内容
        """
        ...

    @abstractmethod
    def validate(self, rule_content: str) -> tuple[bool, str]:
        """验证规则格式。

        Args:
            rule_content: 规则文本

        Returns:
            (是否有效, 消息)
        """
        ...

    @abstractmethod
    def test(self, rule_content: str, pcap_path: str) -> tuple[bool, str]:
        """测试规则是否能检测到 PCAP 中的流量。

        Args:
            rule_content: 规则文本
            pcap_path: PCAP 文件路径

        Returns:
            (是否检测到, 输出信息)
        """
        ...

    @abstractmethod
    def get_schema(self) -> dict:
        """获取规则格式 schema 定义。"""
        ...

    @abstractmethod
    def get_examples(self) -> list[str]:
        """获取示例规则。"""
        ...
