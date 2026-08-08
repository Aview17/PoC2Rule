"""scapy_generator - Scapy PCAP 生成工具。

使用 Scapy 构造网络流量数据包并保存为 PCAP 文件。
"""

import logging
from pathlib import Path

logger = logging.getLogger("poc2rule")


def generate_pcap_with_scapy(
    attack_vector: str = "",
    target_ip: str = "192.168.1.100",
    target_port: int = 80,
    payload: str = "",
    output_path: str = "",
    **kwargs,
) -> dict:
    """使用 Scapy 生成 PCAP 流量文件。

    Args:
        attack_vector: 攻击向量描述
        target_ip: 目标 IP
        target_port: 目标端口
        payload: 攻击载荷
        output_path: 输出文件路径

    Returns:
        执行结果
    """
    logger.info(f"Scapy 生成 PCAP: ip={target_ip}, port={target_port}")

    try:
        from scapy.all import IP, TCP, Raw, wrpcap

        pcap_path = Path(output_path) if output_path else Path("./workspace/pcap/traffic.pcap")
        pcap_path.parent.mkdir(parents=True, exist_ok=True)

        packets = []

        # 源 IP
        src_ip = "10.0.0.1"
        src_port = 12345

        # TCP 三次握手
        syn = IP(src=src_ip, dst=target_ip) / TCP(sport=src_port, dport=target_port, flags="S", seq=1000)
        syn_ack = IP(src=target_ip, dst=src_ip) / TCP(sport=target_port, dport=src_port, flags="SA", seq=2000, ack=1001)
        ack = IP(src=src_ip, dst=target_ip) / TCP(sport=src_port, dport=target_port, flags="A", seq=1001, ack=2001)

        packets.extend([syn, syn_ack, ack])

        # 如果提供了 payload，构造 HTTP 请求
        if payload:
            # Strip payload to use as both the HTTP body and the raw content
            raw_payload = payload.encode("utf-8") if isinstance(payload, str) else payload
            raw_payload = payload if isinstance(payload, bytes) else payload.encode("utf-8")
            http_req = (
                IP(src=src_ip, dst=target_ip) /
                TCP(sport=src_port, dport=target_port, flags="PA", seq=1001, ack=2001) /
                Raw(load=raw_payload)
            )
            packets.append(http_req)
        else:
            # 默认 HTTP GET 请求
            default_payload = (
                f"GET / HTTP/1.1\r\nHost: {target_ip}\r\n"
                "User-Agent: Poc2Rule/1.0\r\n"
                "Accept: */*\r\n\r\n"
            ).encode()
            http_req = (
                IP(src=src_ip, dst=target_ip) /
                TCP(sport=src_port, dport=target_port, flags="PA", seq=1001, ack=2001) /
                Raw(load=default_payload)
            )
            packets.append(http_req)

        # 保存 PCAP
        wrpcap(str(pcap_path), packets)
        logger.info(f"PCAP 已生成: {pcap_path} ({len(packets)} 个数据包)")

        return {
            "success": True,
            "output_path": str(pcap_path),
            "packet_count": len(packets),
        }

    except ImportError:
        logger.error("scapy 未安装")
        return {"error": "scapy 未安装，请执行: pip install scapy"}
    except Exception as e:
        logger.error(f"Scapy 生成失败: {e}")
        return {"error": str(e)}
