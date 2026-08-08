"""PromptBuilder - 负责拼接 Prompt。

任何 Node 都不允许自己拼 Prompt。
读取 SKILL.md、Knowledge、Examples、Input 并自动组合。
"""

import re
from pathlib import Path
from typing import Any


class PromptBuilder:
    """Prompt 构建器，自动组合 SKILL + Knowledge + Examples + Input。"""

    BASE_DIR = Path("inference")

    def build_system_prompt(self, skill_name: str) -> str:
        """构造 system prompt。

        格式：
        SKILL.md
        + Knowledge
        + Examples
        + 输出格式指令
        """
        skill_dir = self.BASE_DIR / skill_name

        parts = []

        # 1. SKILL.md
        skill_path = skill_dir / "SKILL.md"
        if skill_path.exists():
            parts.append(skill_path.read_text(encoding="utf-8"))
        else:
            parts.append(f"# {skill_name}\n\n执行 {skill_name} 任务。")

        # 2. Knowledge
        knowledge_dir = skill_dir / "knowledge"
        if knowledge_dir.exists():
            for kf in sorted(knowledge_dir.glob("*.md")):
                parts.append(f"\n## Knowledge: {kf.stem}\n\n{kf.read_text(encoding='utf-8')}")

        # 3. Examples
        examples_dir = skill_dir / "examples"
        if examples_dir.exists():
            examples_text = self._load_examples(examples_dir)
            if examples_text:
                parts.append(f"\n## Examples\n\n{examples_text}")

        # 4. 输出格式要求
        parts.append("""
## 输出要求

1. 严格输出 JSON 格式
2. 不要包含任何 markdown 代码块标记
3. 不要包含任何解释性文字
4. 所有字段名使用英文 snake_case""")

        return "\n\n---\n\n".join(parts)

    def build_user_prompt(self, skill_name: str, user_input: dict[str, Any]) -> str:
        """构造 user prompt。"""
        import json

        lines = ["## Input\n"]

        for key, value in user_input.items():
            if isinstance(value, str) and len(value) > 500:
                # 长内容，截断显示
                lines.append(f"- **{key}**: (长度: {len(value)} 字符)")
                lines.append(f"```\n{value[:1000]}\n```")
                if len(value) > 1000:
                    lines.append("... (内容已截断)")
            else:
                lines.append(f"- **{key}**: {value}")

        return "\n".join(lines)

    def _load_examples(self, examples_dir: Path) -> str:
        """加载示例文件。"""
        parts = []
        for ef in sorted(examples_dir.glob("*")):
            if ef.suffix in (".json", ".md", ".txt"):
                content = ef.read_text(encoding="utf-8")
                parts.append(f"### Example: {ef.stem}\n\n```\n{content}\n```")
        return "\n\n".join(parts)

    def build_planner_prompt(self, planner_name: str) -> str:
        """构造 Planner 的 system prompt。"""
        planner_path = Path(f"planners/{planner_name}/SKILL.md")
        if planner_path.exists():
            return planner_path.read_text(encoding="utf-8")
        return f"# {planner_name}\n\nPlanner for {planner_name}."
