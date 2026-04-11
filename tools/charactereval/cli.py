"""
人物对话评估命令行入口

支持格式：
1. prompt_payload.json
2. .txt 文件（纯文本角色回答）
3. .json 文件（结构化角色回答）

输出：
1. evaluation_report.json
2. 控制台评估摘要

用法：
    python3 main_character_eval.py --payload data/output/character_chat/jia-baoyu_prompt_payload.json --response "妹妹自然是极好的人。"
    python3 main_character_eval.py --payload data/output/character_chat/jia-baoyu_prompt_payload.json --response-file response.json --output data/eval
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluator import CharacterChatEvaluator


# 默认评估输出目录。
DEFAULT_OUTPUT_DIR = Path("data") / "eval"


def build_parser() -> argparse.ArgumentParser:
    """
    创建人物对话评估命令行参数解析器。

    @params:
        无。

    @return:
        argparse.ArgumentParser 对象。
    """
    parser = argparse.ArgumentParser(description="Evaluate a character reply against prompt payload context.")
    parser.add_argument("--payload", type=Path, required=True, help="Path to prompt_payload.json.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for evaluation reports.")
    parser.add_argument("--response", help="Inline assistant response text.")
    parser.add_argument("--response-file", type=Path, help="Response file in .txt or .json format.")
    parser.add_argument(
        "--cited-passage-id",
        action="append",
        default=[],
        help="Optional cited passage id. Can be used multiple times.",
    )
    return parser


def main() -> None:
    """
    运行人物对话第一版评估流程，并输出结构化报告。

    @params:
        无。参数通过命令行读取。

    @return:
        None。
    """
    args = build_parser().parse_args()
    evaluator = CharacterChatEvaluator()

    report = evaluator.evaluate_from_files(
        payload_file=args.payload,
        response_text=args.response,
        response_file=args.response_file,
        cited_passage_ids=args.cited_passage_id,
    )

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{args.payload.stem}_evaluation.json"
    output_file.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    auto_checks = report.auto_checks

    print("Character chat evaluation completed.")
    print(f"Character: {report.character_name} ({report.character_id})")
    print(f"Query: {report.user_query}")
    print(f"Response length: {auto_checks['response_length_chars']}")
    print(f"Valid citations: {len(auto_checks['valid_citations'])}")
    print(f"Invalid citations: {len(auto_checks['invalid_citations'])}")
    print(f"Modern expression hits: {len(auto_checks['modern_expression_hits'])}")
    print(f"Status: {report.status}")
    print(f"Output: {output_file.resolve()}")
