"""TrafficAnalysisNode - 流量分析节点。

使用 PCAPReader 解析 PCAP 文件。
解析 HTTP、TCP、Payload 等信息。
输出：TrafficInfo
"""

import logging

from app.state import AgentState, TrafficInfo

logger = logging.getLogger("poc2rule")


class TrafficAnalysisNode:
    """流量分析节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("TrafficAnalysisNode: 分析流量")

        if state.error_message:
            logger.warning(f"跳过流量分析，存在错误: {state.error_message}")
            return state

        if not state.pcap_path:
            logger.warning("没有 PCAP 文件，跳过流量分析")
            return state

        # 使用 PCAP Reader 解析
        from tools.pcap_reader import read_pcap
        from tools.http_parser import parse_http_from_pcap

        try:
            packets = read_pcap(state.pcap_path)
            logger.info(f"读取到 {len(packets)} 个数据包")
        except Exception as e:
            logger.error(f"PCAP 读取失败: {e}")
            state.error_message = f"PCAP 读取失败: {e}"
            return state

        # 解析 HTTP 信息
        try:
            http_info = parse_http_from_pcap(packets)
        except Exception as e:
            logger.warning(f"HTTP 解析失败: {e}")
            http_info = {}

        traffic = TrafficInfo(
            src_ip=http_info.get("src_ip", ""),
            dst_ip=http_info.get("dst_ip", ""),
            src_port=http_info.get("src_port", 0),
            dst_port=http_info.get("dst_port", 0),
            protocol=http_info.get("protocol", "TCP"),
            method=http_info.get("method", ""),
            uri=http_info.get("uri", ""),
            headers=http_info.get("headers", {}),
            body=http_info.get("body", ""),
            raw_payload=http_info.get("raw_payload", ""),
        )
        state.traffic_info = traffic

        logger.info(f"流量分析完成: {traffic.method} {traffic.uri}")
        return state
