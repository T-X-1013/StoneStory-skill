"""
《红楼梦》数据构建命令行入口

支持格式：
1. .txt 文件（UTF-8 编码的清洗版《红楼梦》全文）

输出：
1. chapters.json
2. passages.jsonl
3. build_report.json

用法：
    python3 main.py
    python3 main.py --input data/input/StoneStory.txt --output-dir data/output
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .builder import RedMansionCorpusBuilder
from .validation import BuildValidator


# 默认输入文件路径，指向项目内的主文本输入文件。
DEFAULT_INPUT = Path("data") / "input" / "StoneStory.txt"
# 默认输出目录，结构化结果和校验报告都会写到这里。
DEFAULT_OUTPUT_DIR = Path("data") / "output"


def build_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。

    @params:
        无。

    @return:
        argparse.ArgumentParser 对象，用于解析输入路径和输出目录。
    """
    parser = argparse.ArgumentParser(description="Build Hongloumeng dataset outputs.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to the cleaned txt source.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for generated outputs.")
    return parser


def main() -> None:
    """
    运行数据构建与校验流程，并打印结果摘要。

    @params:
        无。参数通过命令行读取。

    @return:
        None。
    """
    args = build_parser().parse_args()
    builder = RedMansionCorpusBuilder()
    validator = BuildValidator()

    # 先生成 chapters.json 和 passages.jsonl。
    result = builder.build(args.input, args.output_dir)
    # 再对输出结果执行结构完整性和异常字符校验。
    validation_result = validator.validate(result, args.output_dir, args.input.parent)

    print("Build completed.")
    print(f"Input: {args.input.resolve()}")
    print(f"Chapters: {len(result.chapters)}")
    print(f"Passages: {len(result.passages)}")
    print(f"chapters.json: {result.chapters_output.resolve()}")
    print(f"passages.jsonl: {result.passages_output.resolve()}")
    print(f"Validation status: {validation_result.status}")
    print(f"build_report.json: {validation_result.report_output.resolve()}")
