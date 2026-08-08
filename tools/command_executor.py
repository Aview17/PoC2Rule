"""command_executor - 通用命令执行工具。

不包含 Prompt。
"""

import logging
import subprocess
from typing import Optional

logger = logging.getLogger("poc2rule")


def run_command(
    command: list[str],
    cwd: Optional[str] = None,
    timeout: int = 60,
    env: Optional[dict] = None,
) -> dict:
    """执行系统命令。

    Args:
        command: 命令列表，例如 ["python", "script.py"]
        cwd: 工作目录
        timeout: 超时秒数
        env: 环境变量

    Returns:
        执行结果字典
    """
    cmd_str = " ".join(command)
    logger.info(f"执行命令: {cmd_str}")

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        logger.error(f"命令超时 ({timeout}s): {cmd_str}")
        return {"success": False, "error": f"命令执行超时 ({timeout}s)"}

    except Exception as e:
        logger.error(f"命令执行异常: {e}")
        return {"success": False, "error": str(e)}
