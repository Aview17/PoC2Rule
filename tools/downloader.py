"""downloader - PoC 下载工具。"""

import logging
from pathlib import Path

import httpx

logger = logging.getLogger("poc2rule")


def download_poc(url: str, save_dir: Path) -> str:
    """从 URL 下载 PoC 文件。

    Args:
        url: PoC 文件 URL
        save_dir: 保存目录

    Returns:
        文件内容字符串
    """
    logger.info(f"下载 PoC: {url}")

    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    content = resp.text

    filename = url.split("/")[-1] or "poc.py"
    filepath = save_dir / filename
    filepath.write_text(content, encoding="utf-8")
    logger.info(f"已保存: {filepath}")

    return content
