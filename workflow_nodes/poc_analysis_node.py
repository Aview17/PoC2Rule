"""PoCAnalysisNode - PoC 分析节点。

调用 InferenceService，分析 PoC 代码，提取关键信息。
输出：PoCAnalysisResult
"""

import logging

from app.state import AgentState, PoCAnalysisResult

logger = logging.getLogger("poc2rule")


class PoCAnalysisNode:
    """PoC 分析节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("PoCAnalysisNode: 分析 PoC")

        if state.error_message:
            logger.warning(f"跳过 PoC 分析，存在错误: {state.error_message}")
            return state

        # 调用 InferenceService
        result = self.ctx.inference_service.run(
            skill_name="poc_analysis",
            user_input={
                "poc_content": state.poc_content,
                "poc_path": state.poc_path,
                "input_type": state.input_type,
            },
        )

        # 填充结果
        analysis = PoCAnalysisResult(
            vuln_type=result.get("vuln_type", ""),
            attack_vector=result.get("attack_vector", ""),
            target_protocol=result.get("target_protocol", ""),
            target_port=result.get("target_port", 0),
            payload_pattern=result.get("payload_pattern", ""),
            description=result.get("description", ""),
        )
        state.poc_analysis = analysis

        logger.info(f"PoC 分析完成: vuln_type={analysis.vuln_type}")
        return state
