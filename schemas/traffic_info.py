"""TrafficInfo 数据模型。"""

from pydantic import BaseModel, Field


class TrafficInfo(BaseModel):
    """流量解析信息模型。"""
    src_ip: str = Field(default="", description="源 IP")
    dst_ip: str = Field(default="", description="目标 IP")
    src_port: int = Field(default=0, description="源端口")
    dst_port: int = Field(default=0, description="目标端口")
    protocol: str = Field(default="TCP", description="协议")
    method: str = Field(default="GET", description="HTTP 方法")
    uri: str = Field(default="/", description="请求 URI")
    headers: dict = Field(default_factory=dict, description="请求头")
    body: str = Field(default="", description="请求体")
    raw_payload: str = Field(default="", description="原始载荷")
