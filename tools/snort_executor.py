"""snort_executor - Snort 执行工具。

用于执行 Snort 命令进行规则测试和验证。
"""

import logging
import subprocess
from pathlib import Path
import tempfile

logger = logging.getLogger("poc2rule")


def snort_validate(rule_content: str, snort_bin: str = "snort", config_path: str = "") -> tuple[bool, str]:
    """验证 Snort 规则语法。

    Args:
        rule_content: 规则内容
        snort_bin: Snort 可执行文件路径
        config_path: Snort 配置路径

    Returns:
        (是否有效, 输出信息)
    """
    logger.info("Snort 规则验证")

    # 写入临时规则文件
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".rules", delete=False, encoding="utf-8"
    ) as f:
        f.write(rule_content)
        rules_file = f.name

    try:
        cmd = [snort_bin, "-T"]
        if config_path:
            cmd.extend(["-c", config_path])
        cmd.extend(["-R", rules_file])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        output = result.stdout + "\n" + result.stderr
        valid = result.returncode == 0

        return valid, output

    except FileNotFoundError:
        logger.warning(f"Snort 未安装或路径错误: {snort_bin}")
        return False, f"Snort 未安装: {snort_bin}"
    except Exception as e:
        logger.error(f"Snort 验证异常: {e}")
        return False, str(e)
    finally:
        Path(rules_file).unlink(missing_ok=True)


def snort_test_replay(
    rule_content: str,
    pcap_path: str,
    snort_bin: str = "snort",
    config_path: str = "",
) -> tuple[bool, str]:
    """使用 Snort 回放 PCAP 测试规则。

    Args:
        rule_content: 规则内容
        pcap_path: PCAP 文件路径
        snort_bin: Snort 可执行文件路径
        config_path: Snort 配置路径

    Returns:
        (是否有告警, 输出信息)
    """
    logger.info(f"Snort 回放测试: pcap={pcap_path}")

    # 写入临时规则文件
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".rules", delete=False, encoding="utf-8"
    ) as f:
        f.write(rule_content)
        rules_file = f.name

    # 创建临时日志目录
    log_dir = tempfile.mkdtemp(prefix="snort_log_")

    try:
        cmd = [
            snort_bin,
            "-r", pcap_path,
            "-c", config_path or "/etc/snort/snort.conf",
            "-R", rules_file,
            "-l", log_dir,
            "-q",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout + "\n" + result.stderr

        # 检查是否有告警
        has_alert = False
        alert_file = Path(log_dir) / "alert"
        if alert_file.exists():
            alert_content = alert_file.read_text()
            has_alert = len(alert_content.strip()) > 0
            if has_alert:
                output += f"\n--- ALERTS ---\n{alert_content}"

        return has_alert, output

    except FileNotFoundError:
        return False, f"Snort 未安装: {snort_bin}"
    except Exception as e:
        return False, str(e)
    finally:
        Path(rules_file).unlink(missing_ok=True)
        # 清理日志目录
        import shutil
        shutil.rmtree(log_dir, ignore_errors=True)
