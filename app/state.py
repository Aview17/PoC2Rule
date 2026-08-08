"""AgentState - 所有 Workflow 节点共享的状态。

至少包含：
- PoC 路径
- PoC 分析结果
- PCAP 路径
- HTTP 流量信息
- 漏洞分类结果
- Detection IR
- 规则列表
- 测试结果
- 最终报告
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PoCAnalysisResult:
    """PoC 分析结果。"""
    vuln_type: str = ""
    attack_vector: str = ""
    target_protocol: str = ""
    target_port: int = 0
    payload_pattern: str = ""
    description: str = ""


@dataclass
class TrafficInfo:
    """HTTP 流量解析信息。"""
    src_ip: str = ""
    dst_ip: str = ""
    src_port: int = 0
    dst_port: int = 0
    protocol: str = ""
    method: str = ""
    uri: str = ""
    headers: dict = field(default_factory=dict)
    body: str = ""
    raw_payload: str = ""


@dataclass
class VulnerabilityInfo:
    """漏洞分类结果。"""
    cwe_id: str = ""
    category: str = ""
    severity: str = ""
    description: str = ""
    affected_component: str = ""


@dataclass
class DetectionIR:
    """中间检测规则 IR。"""
    signatures: list = field(default_factory=list)
    conditions: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class RuleInfo:
    """生成的规则信息。"""
    format: str = ""           # snort / suricata
    content: str = ""          # 规则文本
    path: str = ""             # 规则文件路径
    validated: bool = False
    test_result: Optional[str] = None  # PASS / FAIL
    test_output: str = ""


@dataclass
class AgentState:
    """所有 Workflow 节点共享的状态。"""

    # 输入
    input_type: str = ""       # file / request / url
    poc_path: str = ""         # PoC 文件路径
    poc_url: str = ""          # PoC URL
    poc_content: str = ""      # PoC 原始内容

    # 输出目录
    output_dir: str = ""

    # PoC 分析结果
    poc_analysis: Optional[PoCAnalysisResult] = None

    # PCAP 相关
    pcap_path: str = ""

    # 流量分析
    traffic_info: Optional[TrafficInfo] = None

    # 漏洞分类
    vulnerability_info: Optional[VulnerabilityInfo] = None

    # Detection IR
    detection_ir: Optional[DetectionIR] = None

    # 规则
    rules: list = field(default_factory=list)
    active_plugin: str = "snort"

    # 测试
    test_results: dict = field(default_factory=dict)

    # 报告
    report_path: str = ""

    # 循环控制
    iteration_count: int = 0
    max_iterations: int = 3

    # 错误信息
    error_message: str = ""

    # 工作目录
    workspace_dir: str = "./workspace"

    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "input_type": self.input_type,
            "poc_path": self.poc_path,
            "poc_url": self.poc_url,
            "output_dir": self.output_dir,
            "pcap_path": self.pcap_path,
            "active_plugin": self.active_plugin,
            "iteration_count": self.iteration_count,
            "error_message": self.error_message,
        }
