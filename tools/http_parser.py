"""http_parser - HTTP 流量解析工具。

从 PCAP 解析出的数据包中提取 HTTP 请求/响应信息。
"""

import logging
import re

logger = logging.getLogger("poc2rule")


def parse_http_from_pcap(packets: list[dict]) -> dict:
    """从 PCAP 数据包中解析 HTTP 信息。

    Args:
        packets: PCAP 数据包列表

    Returns:
        HTTP 解析信息字典
    """
    logger.info(f"解析 HTTP 流量: {len(packets)} 个数据包")

    result = {
        "src_ip": "",
        "dst_ip": "",
        "src_port": 0,
        "dst_port": 0,
        "protocol": "TCP",
        "method": "",
        "uri": "",
        "headers": {},
        "body": "",
        "raw_payload": "",
    }

    for pkt in packets:
        src_ip = pkt.get("src_ip", "")
        dst_ip = pkt.get("dst_ip", "")
        src_port = pkt.get("src_port", 0)
        dst_port = pkt.get("dst_port", 0)
        payload = pkt.get("payload_str", "")

        if not payload:
            continue

        # 跳过非 HTTP 的 payload
        if not re.match(r'^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+', payload):
            continue

        result["src_ip"] = src_ip
        result["dst_ip"] = dst_ip
        result["src_port"] = src_port
        result["dst_port"] = dst_port

        # 解析请求行
        lines = payload.split("\r\n")
        if lines:
            req_parts = lines[0].split()
            if len(req_parts) >= 2:
                result["method"] = req_parts[0]
                result["uri"] = req_parts[1]

        # 解析 headers
        is_body = False
        body_lines = []
        for line in lines[1:]:
            if not is_body:
                if line.strip() == "":
                    is_body = True
                    continue
                if ":" in line:
                    key, value = line.split(":", 1)
                    result["headers"][key.strip()] = value.strip()
            else:
                body_lines.append(line)

        result["body"] = "\r\n".join(body_lines)
        result["raw_payload"] = payload

        # 只取第一个 HTTP 请求
        break

    logger.info(f"HTTP 解析完成: {result.get('method', 'N/A')} {result.get('uri', 'N/A')}")
    return result


def parse_http_raw(raw_text: str) -> dict:
    """解析原始 HTTP 请求文本。

    Args:
        raw_text: 原始 HTTP 请求文本

    Returns:
        解析后的 HTTP 信息
    """
    result = {
        "method": "",
        "uri": "",
        "version": "HTTP/1.1",
        "headers": {},
        "body": "",
    }

    if not raw_text:
        return result

    lines = raw_text.strip().split("\n")

    # 请求行
    if lines:
        parts = lines[0].strip().split()
        if len(parts) >= 1:
            result["method"] = parts[0]
        if len(parts) >= 2:
            result["uri"] = parts[1]
        if len(parts) >= 3:
            result["version"] = parts[2]

    # Headers & Body
    is_body = False
    body_lines = []
    for line in lines[1:]:
        line = line.strip()
        if not is_body:
            if line == "":
                is_body = True
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                result["headers"][key.strip()] = value.strip()
        else:
            body_lines.append(line)

    result["body"] = "\n".join(body_lines)
    return result
