"""RuleValidateNode - 规则验证节点。

调用 Plugin 的 Validator 验证规则格式。
例如：Snort -T 语法检查。
"""

import logging

from app.state import AgentState

logger = logging.getLogger("poc2rule")


class RuleValidateNode:
    """规则验证节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("RuleValidateNode: 验证规则")

        if state.error_message:
            logger.warning(f"跳过规则验证，存在错误: {state.error_message}")
            return state

        if not state.rules:
            logger.warning("没有规则可验证")
            return state

        pm = self.ctx.plugin_manager

        for rule in state.rules:
            plugin = pm.get_plugin(rule.format)
            if plugin is None:
                logger.warning(f"未找到插件: {rule.format}")
                rule.validated = False
                continue

            try:
                valid, msg = plugin.validate(rule.content)
                rule.validated = valid
                if valid:
                    logger.info(f"规则验证通过: {rule.format}")
                else:
                    logger.warning(f"规则验证失败 [{rule.format}]: {msg}")
            except Exception as e:
                logger.error(f"规则验证异常: {e}")
                rule.validated = False

        return state
