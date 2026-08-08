"""OutputNode - 输出节点。

汇总所有结果：
1. PCAP
2. Rule
3. Detection IR
4. Report
"""

import json
import logging
from pathlib import Path

from app.state import AgentState

logger = logging.getLogger("poc2rule")


class OutputNode:
    """输出节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("OutputNode: 生成输出")

        output_dir = Path(state.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. 保存 PCAP
        if state.pcap_path and Path(state.pcap_path).exists():
            pcap_dest = output_dir / "traffic.pcap"
            pcap_dest.write_bytes(Path(state.pcap_path).read_bytes())
            state.pcap_path = str(pcap_dest)
            logger.info(f"PCAP 已保存: {pcap_dest}")

        # 2. 保存规则
        for rule in state.rules:
            rule_path = output_dir / f"rule.{rule.format}"
            rule_path.write_text(rule.content, encoding="utf-8")
            rule.path = str(rule_path)
            logger.info(f"规则已保存: {rule_path}")

        # 3. 保存 Detection IR
        if state.detection_ir:
            ir_path = output_dir / "detection_ir.json"
            ir_data = {
                "signatures": state.detection_ir.signatures,
                "conditions": state.detection_ir.conditions,
                "metadata": state.detection_ir.metadata,
            }
            ir_path.write_text(
                json.dumps(ir_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.info(f"Detection IR 已保存: {ir_path}")

        # 4. 生成报告
        report_path = output_dir / "report.json"
        report = self._build_report(state)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        state.report_path = str(report_path)
        logger.info(f"报告已保存: {report_path}")

        return state

    def _build_report(self, state: AgentState) -> dict:
        """构造最终报告。"""
        poc_analysis = {}
        if state.poc_analysis:
            pa = state.poc_analysis
            poc_analysis = {
                "vuln_type": pa.vuln_type,
                "attack_vector": pa.attack_vector,
                "target_protocol": pa.target_protocol,
                "target_port": pa.target_port,
                "payload_pattern": pa.payload_pattern,
                "description": pa.description,
            }

        traffic_info = {}
        if state.traffic_info:
            ti = state.traffic_info
            traffic_info = {
                "src_ip": ti.src_ip,
                "dst_ip": ti.dst_ip,
                "src_port": ti.src_port,
                "dst_port": ti.dst_port,
                "protocol": ti.protocol,
                "method": ti.method,
                "uri": ti.uri,
            }

        vulnerability = {}
        if state.vulnerability_info:
            vi = state.vulnerability_info
            vulnerability = {
                "cwe_id": vi.cwe_id,
                "category": vi.category,
                "severity": vi.severity,
                "description": vi.description,
                "affected_component": vi.affected_component,
            }

        rules_summary = []
        for rule in state.rules:
            rules_summary.append({
                "format": rule.format,
                "path": rule.path,
                "validated": rule.validated,
                "test_result": rule.test_result,
            })

        return {
            "input": {
                "type": state.input_type,
                "source": state.poc_path or state.poc_url,
            },
            "poc_analysis": poc_analysis,
            "pcap": state.pcap_path,
            "traffic_info": traffic_info,
            "vulnerability": vulnerability,
            "detection_ir": {
                "signature_count": len(state.detection_ir.signatures) if state.detection_ir else 0,
                "condition_count": len(state.detection_ir.conditions) if state.detection_ir else 0,
            },
            "rules": rules_summary,
            "iterations": state.iteration_count,
        }
