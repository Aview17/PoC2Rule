"""PoCInfo 数据模型。"""

from pydantic import BaseModel, Field


class PoCInfo(BaseModel):
    """PoC 分析结果模型。"""
    vuln_type: str = Field(description="漏洞类型，如 SQL注入、命令注入、XSS、文件上传等")
    attack_vector: str = Field(description="攻击向量描述")
    target_protocol: str = Field(default="HTTP", description="目标协议")
    target_port: int = Field(default=80, description="目标端口")
    payload_pattern: str = Field(default="", description="攻击载荷特征模式")
    description: str = Field(default="", description="漏洞描述")
