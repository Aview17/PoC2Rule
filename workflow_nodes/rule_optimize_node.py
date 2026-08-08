"""RuleOptimizeNode - 规则优化节点。

当规则测试失败时，调用 Planner 优化规则。
Planner 可以：修改 Detection IR → 重新 Render → 重新 Test。
"""

import logging

from app.state import AgentState

logger = logging.getLogger("poc2rule")


class RuleOptimizeNode:
    """规则优化节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info(f"RuleOptimizeNode: 优化规则 (第 {state.iteration_count + 1} 次)")

        if not state.rules:
            return state

        # 获取当前失败的规则
        failed_rules = [r for r in state.rules if r.test_result == "FAIL"]
        if not failed_rules:
            logger.info("没有失败的规则，无需优化")
            return state

        # 构造 Planner 输入
        failed_rule = failed_rules[0]
        planner_input = {
            "failed_rule": failed_rule.content,
            "format": failed_rule.format,
            "test_output": failed_rule.test_output,
            "detection_ir": {
                "signatures": state.detection_ir.signatures if state.detection_ir else [],
                "conditions": state.detection_ir.conditions if state.detection_ir else [],
                "metadata": state.detection_ir.metadata if state.detection_ir else {},
            },
            "traffic_info": {
                "src_ip": state.traffic_info.src_ip if state.traffic_info else "",
                "dst_ip": state.traffic_info.dst_ip if state.traffic_info else "",
                "src_port": state.traffic_info.src_port if state.traffic_info else 0,
                "dst_port": state.traffic_info.dst_port if state.traffic_info else 0,
                "protocol": state.traffic_info.protocol if state.traffic_info else "",
                "payload": state.traffic_info.raw_payload if state.traffic_info else "",
            },
            "iteration": state.iteration_count,
        }

        # 可用工具
        available_tools = self._build_tools(state)

        # 调用 Planner
        from llm.planner import PlannerService
        planner = PlannerService(self.ctx)

        result = planner.run(
            planner_name="rule_optimizer",
            user_input=planner_input,
            available_tools=available_tools,
        )

        if result.get("error"):
            logger.error(f"规则优化失败: {result['error']}")
            return state

        # 更新 Detection IR（如果 Planner 有修改）
        if "detection_ir" in result:
            from app.state import DetectionIR
            ir_data = result["detection_ir"]
            state.detection_ir = DetectionIR(
                signatures=ir_data.get("signatures", []),
                conditions=ir_data.get("conditions", []),
                metadata=ir_data.get("metadata", {}),
            )

        logger.info("规则优化完成，将重新生成和测试")
        return state

    def _build_tools(self, state: AgentState) -> list:
        """构造优化器可用工具。"""
        return [
            {
                "name": "modify_detection_ir",
                "description": "修改 Detection IR 以修正规则问题。",
                "parameters": {
                    "signatures": "新的签名列表",
                    "conditions": "新的条件列表",
                },
                "function": lambda **kwargs: kwargs,
            },
            {
                "name": "re_render_rule",
                "description": "使用修改后的 Detection IR 重新渲染规则。",
                "parameters": {},
                "function": lambda **kwargs: {
                    "rendered": "规则已通过 Plugin 重新渲染"
                },
            },
        ]
