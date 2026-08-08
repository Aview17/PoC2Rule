"""DetectionGenerateNode - Detection IR 生成节点。

调用 InferenceService，生成中间检测规则 IR。
输出：DetectionIR (signatures, conditions, metadata)
"""

import logging

from app.state import AgentState, DetectionIR

logger = logging.getLogger("poc2rule")


class DetectionGenerateNode:
    """Detection IR 生成节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("DetectionGenerateNode: 生成 Detection IR")

        if state.error_message:
            logger.warning(f"跳过 Detection IR 生成，存在错误: {state.error_message}")
            return state

        # 构造输入
        user_input = {
            "vulnerability": {
                "cwe_id": state.vulnerability_info.cwe_id if state.vulnerability_info else "",
                "category": state.vulnerability_info.category if state.vulnerability_info else "",
                "severity": state.vulnerability_info.severity if state.vulnerability_info else "",
                "description": state.vulnerability_info.description if state.vulnerability_info else "",
            },
            "traffic": {
                "src_ip": state.traffic_info.src_ip if state.traffic_info else "",
                "dst_ip": state.traffic_info.dst_ip if state.traffic_info else "",
                "src_port": state.traffic_info.src_port if state.traffic_info else 0,
                "dst_port": state.traffic_info.dst_port if state.traffic_info else 0,
                "protocol": state.traffic_info.protocol if state.traffic_info else "",
                "method": state.traffic_info.method if state.traffic_info else "",
                "uri": state.traffic_info.uri if state.traffic_info else "",
                "payload": state.traffic_info.raw_payload if state.traffic_info else "",
                "headers": state.traffic_info.headers if state.traffic_info else {},
            },
            "poc_analysis": {
                "vuln_type": state.poc_analysis.vuln_type if state.poc_analysis else "",
                "attack_vector": state.poc_analysis.attack_vector if state.poc_analysis else "",
                "payload_pattern": state.poc_analysis.payload_pattern if state.poc_analysis else "",
            },
        }

        # 调用 InferenceService
        result = self.ctx.inference_service.run(
            skill_name="detection_generate",
            user_input=user_input,
        )

        detection_ir = DetectionIR(
            signatures=result.get("signatures", []),
            conditions=result.get("conditions", []),
            metadata=result.get("metadata", {}),
        )
        state.detection_ir = detection_ir

        logger.info(f"Detection IR 生成完成: {len(detection_ir.signatures)} 个签名")
        return state
