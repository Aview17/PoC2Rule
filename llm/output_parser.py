"""OutputParser - JSON 解析器。

负责从 LLM 原始输出中提取并校验 JSON。
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger("poc2rule")


class OutputParser:
    """输出解析器，从 LLM 响应中提取 JSON。"""

    @staticmethod
    def parse_json(raw_output: str) -> dict[str, Any]:
        """从 LLM 原始输出中解析 JSON。

        支持：
        1. 纯 JSON 字符串
        2. Markdown 代码块中的 JSON
        """
        if not raw_output:
            return {}

        # 尝试直接解析
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        # 尝试从 markdown 代码块中提取
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_output)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试找第一个 { 和最后一个 }
        start = raw_output.find("{")
        end = raw_output.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(raw_output[start:end])
            except json.JSONDecodeError:
                pass

        # 解析失败
        logger.error(f"JSON 解析失败，原始输出: {raw_output[:500]}")
        return {"error": "JSON 解析失败", "raw_output": raw_output[:1000]}

    @staticmethod
    def validate_schema(data: dict, schema: dict) -> tuple[bool, str]:
        """校验 JSON 是否符合 schema（简易校验）。

        Returns:
            (is_valid, message)
        """
        required_fields = schema.get("required", [])

        for field in required_fields:
            if field not in data:
                return False, f"缺少必需字段: {field}"

        return True, "OK"
