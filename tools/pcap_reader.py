"""pcap_reader - PCAP 解析工具。

使用 Scapy 读取 PCAP 文件并提取数据包信息。
"""

import logging
from pathlib import Path

logger = logging.getLogger("poc2rule")


def read_pcap(pcap_path: str) -> list[dict]:
    """读取 PCAP 文件并返回数据包列表。

    Args:
        pcap_path: PCAP 文件路径

    Returns:
        数据包列表，每个元素为字典
    """
    logger.info(f"读取 PCAP: {pcap_path}")

    try:
        from scapy.all import rdpcap, IP, TCP, UDP, Raw
    except ImportError:
        logger.error("scapy 未安装")
        return []

    path = Path(pcap_path)
    if not path.exists():
        logger.error(f"PCAP 文件不存在: {pcap_path}")
        return []

    try:
        packets = rdpcap(str(path))
    except Exception as e:
        logger.error(f"PCAP 解析失败: {e}")
        return []

    result = []
    for pkt in packets:
        info = {"summary": pkt.summary()}

        if IP in pkt:
            info["src_ip"] = pkt[IP].src
            info["dst_ip"] = pkt[IP].dst
            info["protocol"] = "TCP" if TCP in pkt else ("UDP" if UDP in pkt else "IP")

        if TCP in pkt:
            info["src_port"] = pkt[TCP].sport
            info["dst_port"] = pkt[TCP].dport
            info["flags"] = str(pkt[TCP].flags)
        elif UDP in pkt:
            info["src_port"] = pkt[UDP].sport
            info["dst_port"] = pkt[UDP].dport

        if Raw in pkt:
            info["payload"] = pkt[Raw].load
            info["payload_hex"] = pkt[Raw].load.hex()
            info["payload_str"] = pkt[Raw].load.decode("utf-8", errors="replace")

        result.append(info)

    logger.info(f"解析完成: {len(result)} 个数据包")
    return result
