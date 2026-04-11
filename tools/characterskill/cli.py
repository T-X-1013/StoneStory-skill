"""
人物 skill 生成命令行入口

支持格式：
1. manifest.json
2. triples.csv
3. passages.jsonl

输出：
1. 人物 skill 目录下的 relations.md
2. evidence_passages.jsonl
3. evidence_ranked.jsonl
4. style_evidence.jsonl
5. style_summary_candidates.json
6. source_report.json
7. persona.md
8. style.md
9. examples.md

用法：
    python3 main_character_skill.py
    python3 main_character_skill.py --skill-root skill/characters --triples data/input/triples.csv --passages data/output/passages.jsonl
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .builder import CharacterSkillBuilder


# 默认人物 skill 根目录。
DEFAULT_SKILL_ROOT = Path("skill") / "characters"
# 默认关系输入文件。
DEFAULT_TRIPLES_FILE = Path("data") / "input" / "triples.csv"
# 默认原文证据输入文件。
DEFAULT_PASSAGES_FILE = Path("data") / "output" / "passages.jsonl"


def build_parser() -> argparse.ArgumentParser:
    """
    创建人物 skill 生成器的命令行参数解析器。

    @params:
        无。

    @return:
        argparse.ArgumentParser 对象。
    """
    parser = argparse.ArgumentParser(description="Build character skill assets from triples and passages.")
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_SKILL_ROOT, help="Character skill root directory.")
    parser.add_argument("--triples", type=Path, default=DEFAULT_TRIPLES_FILE, help="Path to triples.csv.")
    parser.add_argument("--passages", type=Path, default=DEFAULT_PASSAGES_FILE, help="Path to passages.jsonl.")
    return parser


def main() -> None:
    """
    运行人物 skill 第一版生成流程，并打印结果摘要。

    @params:
        无。参数通过命令行读取。

    @return:
        None。
    """
    args = build_parser().parse_args()
    builder = CharacterSkillBuilder()
    results = builder.build_all(args.skill_root, args.triples, args.passages)

    print("Character skill build completed.")
    print(f"Skill root: {args.skill_root.resolve()}")
    print(f"Triples: {args.triples.resolve()}")
    print(f"Passages: {args.passages.resolve()}")
    for result in results:
        print(
            f"- {result.character_name}: relations={result.relation_count}, "
            f"evidence={result.evidence_count}, ranked={result.ranked_evidence_count}, "
            f"style={result.style_evidence_count}, summaries={result.style_summary_count}, "
            f"report={result.report_output.resolve()}"
        )
