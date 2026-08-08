"""RuleGenerateNode - 规则生成节点。

调用 PluginManager，让选定的 Plugin 渲染生成规则。
Plugin 负责：Renderer → Validator → Tester
输出：规则文本
"""

import logging

from app.state import AgentState, RuleInfo

logger = logging.getLogger("poc2rule")


class RuleGenerateNode:
    """规则生成节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info("RuleGenerateNode: 生成规则")

        if state.error_message:
            logger.warning(f"跳过规则生成，存在错误: {state.error_message}")
            return state

        if not state.detection_ir:
            logger.warning("没有 Detection IR，跳过规则生成")
            return state

        # 获取 Plugin Manager
        pm = self.ctx.plugin_manager

        # 获取当前活跃的 Plugin
        plugin_name = state.active_plugin
        plugin = pm.get_plugin(plugin_name)

        if plugin is None:
            state.error_message = f"未找到插件: {plugin_name}"
            return state

        # 通过 Plugin 渲染规则
        try:
            rule_content = plugin.render(state.detection_ir, self.ctx)

            rule_info = RuleInfo(
                format=plugin_name,
                content=rule_content,
                path="",
            )
            state.rules = [rule_info]

            logger.info(f"规则生成完成: {plugin_name}")
        except Exception as e:
            logger.error(f"规则生成失败: {e}")
            state.error_message = str(e)

        return state
