"""InputNode - 输入节点。

负责：
- 下载 PoC（如果是 URL）
- 读取本地文件
- 解析 HTTP 请求明文
- 保存到 workspace/poc/
"""

import logging
from pathlib import Path
import re

from app.state import AgentState

logger = logging.getLogger("poc2rule")


class InputNode:
    """输入处理节点。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, state: AgentState) -> AgentState:
        logger.info(f"InputNode: 处理输入, type={state.input_type}")

        ws_dir = Path(state.workspace_dir)
        ws_dir.mkdir(parents=True, exist_ok=True)
        poc_dir = ws_dir / "poc"
        poc_dir.mkdir(parents=True, exist_ok=True)

        if state.input_type == "url":
            self._handle_url(state, poc_dir)
        elif state.input_type == "file":
            self._handle_file(state, poc_dir)
        elif state.input_type == "request":
            self._handle_request(state, poc_dir)
        else:
            state.error_message = f"未知输入类型: {state.input_type}"

        return state

    def _handle_url(self, state: AgentState, poc_dir: Path) -> None:
        """从 URL 下载 PoC 文件。"""
        import httpx

        url = state.poc_url
        logger.info(f"下载 PoC: {url}")

        try:
            resp = httpx.get(url, timeout=30, follow_redirects=True)
            resp.raise_for_status()
            content = resp.text

            # 从 URL 提取文件名
            filename = url.split("/")[-1] or "poc.py"
            if not filename.endswith((".py", ".txt")):
                filename += ".txt"

            filepath = poc_dir / filename
            filepath.write_text(content, encoding="utf-8")
            state.poc_path = str(filepath)
            state.poc_content = content
            logger.info(f"PoC 已保存: {filepath}")

        except Exception as e:
            logger.error(f"下载 PoC 失败: {e}")
            state.error_message = f"下载失败: {e}"

    def _handle_file(self, state: AgentState, poc_dir: Path) -> None:
        """读取本地 PoC 文件。"""
        path = Path(state.poc_path)
        if not path.exists():
            state.error_message = f"文件不存在: {state.poc_path}"
            return

        content = path.read_text(encoding="utf-8")
        state.poc_content = content

        # 复制到 workspace
        dest = poc_dir / path.name
        dest.write_text(content, encoding="utf-8")
        state.poc_path = str(dest)
        logger.info(f"PoC 已复制: {dest}")

    def _handle_request(self, state: AgentState, poc_dir: Path) -> None:
        """解析 HTTP 请求明文。"""
        path = Path(state.poc_path)
        if not path.exists():
            state.error_message = f"文件不存在: {state.poc_path}"
            return

        content = path.read_text(encoding="utf-8")
        state.poc_content = content

        # 保存到 workspace
        dest = poc_dir / path.name
        dest.write_text(content, encoding="utf-8")
        state.poc_path = str(dest)

        # 尝试解析 HTTP 请求
        if self._is_http_request(content):
            logger.info("检测到 HTTP 请求明文，将包装为 PoC 脚本")
            wrapped = self._wrap_http_request(content)
            poc_file = poc_dir / "wrapped_poc.py"
            poc_file.write_text(wrapped, encoding="utf-8")
            state.poc_content = wrapped
            logger.info(f"HTTP 请求已包装为 PoC: {poc_file}")

        logger.info(f"HTTP 请求已保存: {dest}")

    def _is_http_request(self, content: str) -> bool:
        """判断内容是否为 HTTP 请求明文。"""
        return bool(re.match(r'^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+', content.strip()))

    def _wrap_http_request(self, content: str) -> str:
        """将 HTTP 请求明文包装为 Python PoC。"""
        return '''"""Auto-generated PoC from HTTP request."""

import os
import requests

raw_request = """{content}"""

# 解析 HTTP 请求
lines = raw_request.strip().split("\\n")
request_line = lines[0].split()
method = request_line[0] if len(request_line) > 0 else "GET"
path = request_line[1] if len(request_line) > 1 else "/"

# 解析 headers 和 body
headers = {{}}
body = ""
is_body = False
headers_end = False
for line in lines[1:]:
    if not headers_end:
        if line.strip() == "":
            headers_end = True
            is_body = True
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
    else:
        body += line + "\\n"

# 发送请求（通过环境变量 TARGET_HOST 指定目标）
target_host = os.environ.get("TARGET_HOST", "127.0.0.1")
target_url = f"http://{{target_host}}{{path}}"
if method == "POST":
    resp = requests.post(target_url, headers=headers, data=body, timeout=10)
else:
    resp = requests.get(target_url, headers=headers, timeout=10)

print(f"Status: {{resp.status_code}}")
print(f"Response: {{resp.text[:500]}}")
'''.format(content=content)
