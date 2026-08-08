"""DetectionIR 数据模型。"""

from pydantic import BaseModel, Field


class Signature(BaseModel):
    """检测签名。"""
    name: str = Field(default="", description="签名名称")
    pattern: str = Field(default="", description="匹配模式")
    type: str = Field(default="content", description="类型: content / pcre / regex")
    modifiers: dict = Field(default_factory=dict, description="修饰符: nocase, depth, offset, distance, within 等")


class Condition(BaseModel):
    """检测条件。"""
    field: str = Field(default="", description="字段名")
    operator: str = Field(default="equals", description="运算符: equals, contains, regex, gt, lt")
    value: str = Field(default="", description="期望值")


class DetectionIR(BaseModel):
    """中间检测规则 IR。"""
    signatures: list[Signature] = Field(default_factory=list, description="检测签名列表")
    conditions: list[Condition] = Field(default_factory=list, description="检测条件列表")
    metadata: dict = Field(default_factory=dict, description="元数据")
