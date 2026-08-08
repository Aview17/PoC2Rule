"""PlannerService - Planner Agent。

Planner 是局部 Agent，仅负责当前节点如何完成。
可以循环调用 Tool，根据 Observation 修改策略。

返回最终结果。
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("poc2rule")


class PlannerService:
    """Planner Agent - 局部决策代理。

    负责单个节点的策略规划，支持：
    - 循环调用 Tool
    - 根据 Observation 修改策略
    """

    MAX_ITERATIONS = 10

    def __init__(self, ctx):
        self.ctx = ctx

    def run(
        self,
        planner_name: str,
        user_input: dict[str, Any],
        available_tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """执行 Planner Agent。

        Args:
            planner_name: Planner 名称（对应 planners/{planner_name}/SKILL.md）
            user_input: 用户输入
            available_tools: 可用工具列表，每个工具包含 name, description, parameters

        Returns:
            最终结果
        """
        planner_skill_path = Path(f"planners/{planner_name}/SKILL.md")
        if planner_skill_path.exists():
            skill_content = planner_skill_path.read_text(encoding="utf-8")
        else:
            skill_content = self._default_planner_skill()

        tool_descriptions = self._format_tools(available_tools)

        system_prompt = f"""{skill_content}

## 可用工具

{tool_descriptions}

## 输出格式

每次响应必须是以下 JSON 格式之一：

如果需要调用工具：
{{"action": "tool", "tool_name": "工具名", "tool_args": {{...}}}}

如果任务完成：
{{"action": "finish", "result": {{...}}}}

请逐步分析并执行。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_input, ensure_ascii=False, indent=2)},
        ]

        # Agent 循环
        for i in range(self.MAX_ITERATIONS):
            logger.debug(f"Planner [{planner_name}] 第 {i+1} 轮")

            response = self.ctx.llm_client.chat(messages)

            parsed = self._parse_planner_response(response)
            if parsed is None:
                logger.error(f"Planner 响应解析失败: {response}")
                continue

            action = parsed.get("action", "")

            if action == "finish":
                logger.info(f"Planner [{planner_name}] 完成")
                return parsed.get("result", {})

            elif action == "tool":
                tool_name = parsed.get("tool_name", "")
                tool_args = parsed.get("tool_args", {})

                logger.info(f"Planner 调用工具: {tool_name}")

                # 执行工具
                observation = self._execute_tool(tool_name, tool_args, available_tools)

                # 追加 Observation 到消息历史
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": f"Observation:\n{json.dumps(observation, ensure_ascii=False, indent=2)}"
                })

        logger.error(f"Planner [{planner_name}] 达到最大迭代次数")
        return {"error": "达到最大迭代次数", "partial_result": {}}

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _default_planner_skill(self) -> str:
        return """你是一个 Planner Agent，负责完成单个子任务。

你会被赋予一组 Tool，你需要一步步使用这些 Tool 来完成任务。

规则：
1. 一次只调用一个 Tool
2. 根据 Observation 调整策略
3. 任务完成后返回 finish
4. 如果无法完成，返回 finish 并说明原因"""

    def _format_tools(self, tools: list[dict]) -> str:
        lines = []
        for tool in tools:
            lines.append(f"- **{tool.get('name', '')}**: {tool.get('description', '')}")
            params = tool.get("parameters", {})
            if params:
                lines.append(f"  参数: {json.dumps(params, ensure_ascii=False)}")
        return "\n".join(lines)

    def _parse_planner_response(self, response: str) -> dict | None:
        """解析 Planner 的 JSON 响应。"""
        try:
            # 尝试提取 JSON 块
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试从 markdown 代码块中提取
            import re
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
        return None

    def _execute_tool(
        self,
        tool_name: str,
        tool_args: dict,
        available_tools: list[dict],
    ) -> dict:
        """执行指定的工具。"""
        tool = next((t for t in available_tools if t.get("name") == tool_name), None)
        if tool is None:
            return {"error": f"未知工具: {tool_name}"}

        func = tool.get("function")
        if func is None:
            return {"error": f"工具 {tool_name} 没有可执行函数"}

        try:
            result = func(**tool_args)
            return {"result": result}
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {e}")
            return {"error": str(e)}
