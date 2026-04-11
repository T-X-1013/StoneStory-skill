"""
人物对话命令行入口

支持格式：
1. 人物 skill 目录资产
2. evidence_ranked.jsonl
3. style_evidence.jsonl

输出：
1. prompt_payload.json
2. 控制台检索摘要

用法：
    python3 main_character_chat.py --character-id jia-baoyu --query "你怎么看黛玉？"
    python3 main_character_chat.py --character-id lin-daiyu --query "你为什么总是伤感？" --output data/output/character_chat
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .prompt_builder import CharacterChatPromptBuilder
from .retriever import CharacterChatRetriever


# 默认人物 skill 根目录。
DEFAULT_SKILL_ROOT = Path("skill") / "characters"
# 默认 prompt payload 输出目录。
DEFAULT_OUTPUT_DIR = Path("data") / "output" / "character_chat"


def build_parser() -> argparse.ArgumentParser:
    """
    创建人物对话命令行参数解析器。

    @params:
        无。

    @return:
        argparse.ArgumentParser 对象。
    """
    parser = argparse.ArgumentParser(description="Build character chat prompt payload from skill assets.")
    parser.add_argument("--character-id", required=True, help="Character id defined in manifest.json.")
    parser.add_argument("--query", required=True, help="User query for the character.")
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_SKILL_ROOT, help="Character skill root directory.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for prompt payload output.")
    parser.add_argument("--style-top-k", type=int, default=3, help="Number of style evidence items to include.")
    parser.add_argument("--fact-top-k", type=int, default=5, help="Number of factual evidence items to include.")
    parser.add_argument("--relation-top-k", type=int, default=8, help="Number of relation items to include.")
    return parser


def main() -> None:
    """
    运行人物对话第一阶段的检索与 prompt payload 生成流程。

    @params:
        无。参数通过命令行读取。

    @return:
        None。
    """
    args = build_parser().parse_args()
    retriever = CharacterChatRetriever()
    prompt_builder = CharacterChatPromptBuilder()

    retrieval_result = retriever.retrieve(
        skill_root=args.skill_root,
        character_id=args.character_id,
        user_query=args.query,
        style_top_k=args.style_top_k,
        fact_top_k=args.fact_top_k,
        relation_top_k=args.relation_top_k,
    )
    prompt_payload = prompt_builder.build_prompt_payload(retrieval_result)

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{args.character_id}_prompt_payload.json"
    output_file.write_text(json.dumps(prompt_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    style_count = len(prompt_payload["context"]["retrieval"]["style_evidence"])
    fact_count = len(prompt_payload["context"]["retrieval"]["fact_evidence"])
    relation_count = len(prompt_payload["context"]["retrieval"]["relations"])

    print("Character chat payload completed.")
    print(f"Character: {prompt_payload['character']['name']} ({prompt_payload['character']['id']})")
    print(f"Query: {args.query}")
    print(f"Style evidence: {style_count}")
    print(f"Fact evidence: {fact_count}")
    print(f"Relations: {relation_count}")
    print(f"Output: {output_file.resolve()}")
