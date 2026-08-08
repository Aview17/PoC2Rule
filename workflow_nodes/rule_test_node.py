"""RuleTestNode - 规则测试节点。

调用 Plugin 的 Tester 测试规则。
例如：Snort Replay 测试。
"""

import logging

from app.state import AgentState

logger = logging.getLogger("poc2rule")


class RuleTestNode:
    """规则测试节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("RuleTestNode: 测试规则")

        if state.error_message:
            logger.warning(f"跳过规则测试，存在错误: {state.error_message}")
            return state

        if not state.rules:
            logger.warning("没有规则可测试")
            return state

        pm = self.ctx.plugin_manager

        for rule in state.rules:
            plugin = pm.get_plugin(rule.format)
            if plugin is None:
                logger.warning(f"未找到插件: {rule.format}")
                rule.test_result = "FAIL"
                continue

            try:
                result, output = plugin.test(
                    rule_content=rule.content,
                    pcap_path=state.pcap_path,
                )
                rule.test_result = "PASS" if result else "FAIL"
                rule.test_output = output
                logger.info(f"规则测试: {rule.test_result} [{rule.format}]")
            except Exception as e:
                logger.error(f"规则测试异常: {e}")
                rule.test_result = "FAIL"
                rule.test_output = str(e)

        state.test_results = {
            rule.format: {
                "result": rule.test_result,
                "output": rule.test_output,
            }
            for rule in state.rules
        }

        return state
