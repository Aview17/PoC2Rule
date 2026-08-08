"""Snort Plugin - Snort 规则插件。

实现 PluginBase 接口：
- Renderer: 使用 LLM 将 Detection IR 渲染为 Snort 规则
- Validator: 使用 snort -T 验证语法
- Tester: 使用 snort 回放 PCAP 测试规则
"""

import json
import logging
from pathlib import Path
from typing import Any

from plugins.base import PluginBase

logger = logging.getLogger("poc2rule")


class Plugin(PluginBase):
    """Snort 规则插件。"""

    def __init__(self, config: dict):
        self.config = config
        self.snort_bin = config.get("snort_bin", "snort")
        self.snort_config = config.get("config_path", "/etc/snort/snort.conf")

    @property
    def name(self) -> str:
        return "snort"

    def render(self, detection_ir: Any, ctx: Any) -> str:
        """使用 LLM 将 Detection IR 渲染为 Snort 规则。

        读取 schema.md、examples，由 LLM 生成规则。
        """
        logger.info("Snort Renderer: 渲染规则")

        # 读取 schema
        schema_path = Path(__file__).parent / "schema.md"
        schema_content = ""
        if schema_path.exists():
            schema_content = schema_path.read_text(encoding="utf-8")

        # 读取示例
        examples = self._load_examples()

        # 构造 Prompt
        system_prompt = f"""{schema_content}

## Examples

{examples}

## 输出要求

1. 严格输出 Snort 规则文本
2. 每条规则一行
3. 不要包含 markdown 标记
4. 规则必须完整、可被 snort -T 验证通过"""

        user_prompt = f"""## Detection IR

```json
{json.dumps(detection_ir.signatures, ensure_ascii=False, indent=2)}
```

## Conditions

```json
{json.dumps(detection_ir.conditions, ensure_ascii=False, indent=2)}
```

## Metadata

```json
{json.dumps(detection_ir.metadata, ensure_ascii=False, indent=2)}
```

请根据以上 Detection IR 生成 Snort 规则。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        raw_output = ctx.llm_client.chat(messages)

        # 清理输出（去除 markdown 标记）
        import re
        cleaned = re.sub(r'```[a-zA-Z]*\n?', '', raw_output)
        cleaned = cleaned.strip()

        return cleaned

    def validate(self, rule_content: str) -> tuple[bool, str]:
        """使用 snort -T 验证规则语法。"""
        logger.info("Snort Validator: 验证规则")

        from tools.snort_executor import snort_validate
        return snort_validate(
            rule_content=rule_content,
            snort_bin=self.snort_bin,
            config_path=self.snort_config,
        )

    def test(self, rule_content: str, pcap_path: str) -> tuple[bool, str]:
        """使用 Snort 回放 PCAP 测试规则。"""
        logger.info(f"Snort Tester: 测试规则, pcap={pcap_path}")

        from tools.snort_executor import snort_test_replay
        return snort_test_replay(
            rule_content=rule_content,
            pcap_path=pcap_path,
            snort_bin=self.snort_bin,
            config_path=self.snort_config,
        )

    def get_schema(self) -> dict:
        """获取 Snort 规则 schema。"""
        return {
            "format": "snort",
            "fields": [
                "action", "protocol", "src_ip", "src_port",
                "direction", "dst_ip", "dst_port", "options",
            ],
            "options": [
                "msg", "content", "depth", "offset", "distance", "within",
                "nocase", "flow", "classtype", "sid", "rev",
            ],
        }

    def get_examples(self) -> list[str]:
        """获取示例 Snort 规则。"""
        examples = self._load_examples()
        return examples.split("\n\n") if examples else []

    def _load_examples(self) -> str:
        """从文件加载示例规则。"""
        examples_dir = Path(__file__).parent / "examples"
        if examples_dir.exists():
            parts = []
            for ef in sorted(examples_dir.glob("*.rules")):
                parts.append(ef.read_text(encoding="utf-8"))
            return "\n\n".join(parts)
        return self._default_examples()

    def _default_examples(self) -> str:
        return """# SQL Injection
alert tcp $EXTERNAL_NET any -> $HTTP_SERVERS $HTTP_PORTS (
  msg:"SQL Injection Attempt";
  flow:to_server,established;
  content:"SELECT"; nocase;
  content:"FROM"; nocase; distance:0;
  classtype:web-application-attack;
  sid:1000001; rev:1;
)

# XSS Attack
alert tcp $EXTERNAL_NET any -> $HTTP_SERVERS $HTTP_PORTS (
  msg:"XSS Attack Attempt";
  flow:to_server,established;
  content:"<script>"; nocase;
  classtype:web-application-attack;
  sid:1000002; rev:1;
)"""
