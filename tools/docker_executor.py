"""docker_executor - Docker 执行工具。

在 Docker 容器中运行 PoC 并抓包。
"""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger("poc2rule")


def generate_pcap_with_docker(
    poc_content: str = "",
    target: str = "",
    output_path: str = "",
    **kwargs,
) -> dict:
    """在 Docker 容器中运行 PoC 并捕获流量。

    Args:
        poc_content: PoC 脚本内容
        target: 目标地址
        output_path: PCAP 输出路径

    Returns:
        执行结果
    """
    logger.info(f"Docker 生成 PCAP: target={target}, output={output_path}")

    if not poc_content:
        return {"error": "PoC 内容为空"}

    # 写入临时 PoC 文件
    tmp_dir = Path("/tmp/poc2rule_docker")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    poc_file = tmp_dir / "poc.py"
    poc_file.write_text(poc_content, encoding="utf-8")

    output_file = Path(output_path) if output_path else tmp_dir / "traffic.pcap"

    try:
        # 启动 Docker 容器并运行 PoC
        cmd = [
            "docker", "run", "--rm",
            "--network", "host",
            "-v", f"{tmp_dir}:/poc:ro",
            "-v", f"{output_file.parent}:/output",
            "poc2rule-runner:latest",
            "python", "/poc/poc.py",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_path": str(output_file),
        }
    except subprocess.TimeoutExpired:
        return {"error": "Docker 执行超时"}
    except Exception as e:
        logger.error(f"Docker 执行失败: {e}")
        return {"error": str(e)}


def run_in_docker(image: str, command: list[str], timeout: int = 60) -> dict:
    """在 Docker 容器中执行任意命令。

    Args:
        image: Docker 镜像名
        command: 命令列表
        timeout: 超时秒数

    Returns:
        执行结果
    """
    logger.info(f"Docker 执行: {image} {' '.join(command)}")

    try:
        cmd = ["docker", "run", "--rm", image] + command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {"error": "命令执行超时"}
    except Exception as e:
        return {"error": str(e)}
