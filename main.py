"""PoC2Rule Agent - 程序入口。

读取输入 → 创建 AgentState → 启动 Workflow。
不包含任何业务逻辑。
"""

import argparse
import sys
from pathlib import Path

from app.state import AgentState
from app.context import AppContext
from app.logger import setup_logger
from workflow import PoC2RuleWorkflow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PoC2Rule Agent - 将 PoC 转换为检测规则"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--poc", "-p", type=str,
        help="本地 PoC 文件路径 (poc.py)"
    )
    group.add_argument(
        "--request", "-r", type=str,
        help="HTTP 请求明文文件路径 (request.txt)"
    )
    group.add_argument(
        "--url", "-u", type=str,
        help="PoC 文件 URL (例如 https://xxx.com/poc.py)"
    )
    parser.add_argument(
        "--output", "-o", type=str, default="./workspace/output",
        help="输出目录 (默认: ./workspace/output)"
    )
    parser.add_argument(
        "--config", "-c", type=str, default="config.yaml",
        help="配置文件路径 (默认: config.yaml)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="详细输出"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # 初始化上下文和日志
    ctx = AppContext(config_path=args.config)
    logger = setup_logger(ctx.config)
    logger.info("PoC2Rule Agent 启动")

    # 创建 AgentState
    state = AgentState()

    # 设置输入来源
    if args.poc:
        state.poc_path = args.poc
        state.input_type = "file"
    elif args.request:
        state.poc_path = args.request
        state.input_type = "request"
    elif args.url:
        state.poc_url = args.url
        state.input_type = "url"
        state.poc_path = args.url  # 先用 URL 作为标识

    state.output_dir = args.output

    logger.info(f"输入类型: {state.input_type}, 输入: {args.poc or args.request or args.url}")

    # 启动 Workflow
    try:
        workflow = PoC2RuleWorkflow(ctx)
        final_state = workflow.run(state)
        logger.info("Workflow 完成")
        logger.info(f"输出目录: {final_state.output_dir}")

        # 打印结果摘要
        print("\n" + "=" * 60)
        print("PoC2Rule Agent - 执行完成")
        print("=" * 60)
        if final_state.pcap_path:
            print(f"  PCAP:       {final_state.pcap_path}")
        if final_state.rules:
            print(f"  规则数量:     {len(final_state.rules)}")
            for r in final_state.rules:
                print(f"    - {r.format}: {r.path}")
        if final_state.detection_ir:
            print(f"  Detection IR: 已生成")
        if final_state.report_path:
            print(f"  报告:       {final_state.report_path}")
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Workflow 执行失败: {e}", exc_info=True)
        print(f"\n错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
