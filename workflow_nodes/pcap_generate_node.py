"""PCAPGenerateNode - PCAP 生成节点。

调用 Planner，决定 PCAP 生成策略（Scapy / Docker / Hook 等）。
Planner 可以循环调用多个 Tool。
输出：PCAP 文件路径
"""

import logging
from pathlib import Path

from app.state import AgentState

logger = logging.getLogger("poc2rule")


class PCAPGenerateNode:
    """PCAP 生成节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("PCAPGenerateNode: 生成 PCAP")

        if state.error_message:
            logger.warning(f"跳过 PCAP 生成，存在错误: {state.error_message}")
            return state

        # 确保 PCAP 输出目录
        pcap_dir = Path(state.workspace_dir) / "pcap"
        pcap_dir.mkdir(parents=True, exist_ok=True)
        pcap_path = pcap_dir / "traffic.pcap"

        # 构造 Planner 输入
        planner_input = {
            "poc_content": state.poc_content,
            "poc_analysis": {
                "vuln_type": state.poc_analysis.vuln_type if state.poc_analysis else "",
                "attack_vector": state.poc_analysis.attack_vector if state.poc_analysis else "",
                "target_protocol": state.poc_analysis.target_protocol if state.poc_analysis else "",
                "target_port": state.poc_analysis.target_port if state.poc_analysis else 0,
                "payload_pattern": state.poc_analysis.payload_pattern if state.poc_analysis else "",
            },
            "output_path": str(pcap_path),
        }

        # 可用工具
        available_tools = self._build_tools(pcap_path)

        # 调用 Planner
        from llm.planner import PlannerService
        planner = PlannerService(self.ctx)

        result = planner.run(
            planner_name="pcap_planner",
            user_input=planner_input,
            available_tools=available_tools,
        )

        if result.get("error"):
            logger.error(f"PCAP 生成失败: {result['error']}")
            state.error_message = result["error"]
            return state

        # 检查 PCAP 文件是否生成
        if pcap_path.exists():
            state.pcap_path = str(pcap_path)
            logger.info(f"PCAP 已生成: {pcap_path}")
        else:
            logger.warning("PCAP 文件未生成")
            state.pcap_path = str(pcap_path)

        return state

    def _build_tools(self, pcap_path: Path) -> list:
        """构造 Planner 可用工具列表。"""
        from tools.scapy_generator import generate_pcap_with_scapy
        from tools.docker_executor import generate_pcap_with_docker

        return [
            {
                "name": "scapy_generate",
                "description": "使用 Scapy 生成 PCAP 流量文件。适用于已知流量模式的场景。",
                "parameters": {
                    "attack_vector": "攻击向量描述",
                    "target_ip": "目标 IP",
                    "target_port": "目标端口",
                    "payload": "攻击载荷",
                    "output_path": "输出文件路径",
                },
                "function": lambda **kwargs: generate_pcap_with_scapy(output_path=str(pcap_path), **kwargs),
            },
            {
                "name": "docker_generate",
                "description": "在 Docker 容器中运行 PoC 并抓包。适用于需要真实网络环境的场景。",
                "parameters": {
                    "poc_content": "PoC 原始内容",
                    "target": "目标地址",
                    "output_path": "输出文件路径",
                },
                "function": lambda **kwargs: generate_pcap_with_docker(output_path=str(pcap_path), **kwargs),
            },
        ]
