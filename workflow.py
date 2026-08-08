"""Workflow - 定义 LangGraph 工作流。

负责：
- 定义所有 Node
- 定义节点之间的流转关系

Workflow 不直接调用 LLM，只调用 Node。
"""

import logging
from typing import Literal

from langgraph.graph import StateGraph, END

from app.state import AgentState
from app.context import AppContext

from workflow_nodes.input_node import InputNode
from workflow_nodes.poc_analysis_node import PoCAnalysisNode
from workflow_nodes.pcap_generate_node import PCAPGenerateNode
from workflow_nodes.traffic_analysis_node import TrafficAnalysisNode
from workflow_nodes.vulnerability_classify_node import VulnerabilityClassifyNode
from workflow_nodes.detection_generate_node import DetectionGenerateNode
from workflow_nodes.rule_generate_node import RuleGenerateNode
from workflow_nodes.rule_validate_node import RuleValidateNode
from workflow_nodes.rule_test_node import RuleTestNode
from workflow_nodes.rule_optimize_node import RuleOptimizeNode
from workflow_nodes.output_node import OutputNode


logger = logging.getLogger("poc2rule")


class PoC2RuleWorkflow:
    """PoC2Rule 主工作流。"""

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.graph = self._build_graph()

    # ------------------------------------------------------------------
    # Node 定义（委托给各 Node 实例）
    # ------------------------------------------------------------------

    def _input_node(self, state: AgentState) -> AgentState:
        return InputNode(self.ctx).execute(state)

    def _poc_analysis_node(self, state: AgentState) -> AgentState:
        return PoCAnalysisNode(self.ctx).execute(state)

    def _pcap_generate_node(self, state: AgentState) -> AgentState:
        return PCAPGenerateNode(self.ctx).execute(state)

    def _traffic_analysis_node(self, state: AgentState) -> AgentState:
        return TrafficAnalysisNode(self.ctx).execute(state)

    def _vulnerability_classify_node(self, state: AgentState) -> AgentState:
        return VulnerabilityClassifyNode(self.ctx).execute(state)

    def _detection_generate_node(self, state: AgentState) -> AgentState:
        return DetectionGenerateNode(self.ctx).execute(state)

    def _rule_generate_node(self, state: AgentState) -> AgentState:
        return RuleGenerateNode(self.ctx).execute(state)

    def _rule_validate_node(self, state: AgentState) -> AgentState:
        return RuleValidateNode(self.ctx).execute(state)

    def _rule_test_node(self, state: AgentState) -> AgentState:
        return RuleTestNode(self.ctx).execute(state)

    def _rule_optimize_node(self, state: AgentState) -> AgentState:
        return RuleOptimizeNode(self.ctx).execute(state)

    def _output_node(self, state: AgentState) -> AgentState:
        return OutputNode(self.ctx).execute(state)

    # ------------------------------------------------------------------
    # 路由
    # ------------------------------------------------------------------

    def _route_after_test(self, state: AgentState) -> Literal["rule_optimize_node", "output_node"]:
        """根据测试结果决定下一步。"""
        if state.iteration_count >= state.max_iterations:
            logger.warning(f"达到最大迭代次数 {state.max_iterations}，跳过优化")
            return "output_node"

        # 检查是否有规则测试失败
        for rule in state.rules:
            if rule.test_result == "FAIL":
                logger.info("规则测试失败，进入优化节点")
                state.iteration_count += 1
                return "rule_optimize_node"

        logger.info("所有规则测试通过")
        return "output_node"

    # ------------------------------------------------------------------
    # 构建图
    # ------------------------------------------------------------------

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        # 添加节点
        graph.add_node("input_node", self._input_node)
        graph.add_node("poc_analysis_node", self._poc_analysis_node)
        graph.add_node("pcap_generate_node", self._pcap_generate_node)
        graph.add_node("traffic_analysis_node", self._traffic_analysis_node)
        graph.add_node("vulnerability_classify_node", self._vulnerability_classify_node)
        graph.add_node("detection_generate_node", self._detection_generate_node)
        graph.add_node("rule_generate_node", self._rule_generate_node)
        graph.add_node("rule_validate_node", self._rule_validate_node)
        graph.add_node("rule_test_node", self._rule_test_node)
        graph.add_node("rule_optimize_node", self._rule_optimize_node)
        graph.add_node("output_node", self._output_node)

        # 定义边（线性流程）
        graph.add_edge("input_node", "poc_analysis_node")
        graph.add_edge("poc_analysis_node", "pcap_generate_node")
        graph.add_edge("pcap_generate_node", "traffic_analysis_node")
        graph.add_edge("traffic_analysis_node", "vulnerability_classify_node")
        graph.add_edge("vulnerability_classify_node", "detection_generate_node")
        graph.add_edge("detection_generate_node", "rule_generate_node")
        graph.add_edge("rule_generate_node", "rule_validate_node")
        graph.add_edge("rule_validate_node", "rule_test_node")

        # 条件分支：测试通过 → 输出，测试失败 → 优化
        graph.add_conditional_edges(
            "rule_test_node",
            self._route_after_test,
            {
                "rule_optimize_node": "rule_optimize_node",
                "output_node": "output_node",
            }
        )
        graph.add_edge("rule_optimize_node", "rule_generate_node")
        graph.add_edge("output_node", END)

        # 设置入口
        graph.set_entry_point("input_node")

        return graph.compile()

    # ------------------------------------------------------------------
    # 运行
    # ------------------------------------------------------------------

    def run(self, state: AgentState) -> AgentState:
        """执行工作流。"""
        logger.info("启动 Workflow")
        result = self.graph.invoke(state)
        logger.info("Workflow 完成")
        return result
