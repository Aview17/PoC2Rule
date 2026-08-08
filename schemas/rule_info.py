"""RuleInfo 数据模型。"""

from pydantic import BaseModel, Field
from typing import Optional


class RuleInfo(BaseModel):
    """规则信息模型。"""
    format: str = Field(default="snort", description="规则格式: snort / suricata")
    content: str = Field(default="", description="规则文本内容")
    path: str = Field(default="", description="规则文件路径")
    validated: bool = Field(default=False, description="是否通过验证")
    test_result: Optional[str] = Field(default=None, description="测试结果: PASS / FAIL")
    test_output: str = Field(default="", description="测试输出")
