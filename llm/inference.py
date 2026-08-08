"""InferenceService - 统一提供一次推理接口。

不负责 Tool 调度，不循环。
输入: skill, knowledge, examples, input, output_schema
输出: JSON 对象
"""

import json
import logging
from typing import Any, Optional

from llm.prompt_builder import PromptBuilder
from llm.output_parser import OutputParser

logger = logging.getLogger("poc2rule")


class InferenceService:
    """一次 LLM 推理服务。"""

    def __init__(self, ctx):
        self.ctx = ctx
        self._prompt_builder = None

    @property
    def prompt_builder(self) -> PromptBuilder:
        if self._prompt_builder is None:
            self._prompt_builder = PromptBuilder()
        return self._prompt_builder

    def run(
        self,
        skill_name: str,
        user_input: dict[str, Any],
        output_schema: Optional[dict] = None,
    ) -> dict[str, Any]:
        """执行一次 LLM 推理。

        Args:
            skill_name: 技能名称（对应 inference/{skill_name}/ 下的 SKILL.md）
            user_input: 用户输入数据
            output_schema: 期望的 JSON schema

        Returns:
            解析后的 JSON 对象
        """
        # 1. 构造 Prompt
        system_prompt = self.prompt_builder.build_system_prompt(skill_name)
        user_prompt = self.prompt_builder.build_user_prompt(skill_name, user_input)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        logger.info(f"Inference 调用: skill={skill_name}")

        # 2. 调用 LLM（强制 JSON 输出）
        raw_output = self.ctx.llm_client.chat_json(messages)

        # 3. 解析输出
        result = OutputParser.parse_json(raw_output)
        logger.debug(f"Inference 结果: {json.dumps(result, ensure_ascii=False)[:500]}")

        return result
