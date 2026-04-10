"""
《红楼梦》数据构建校验器

支持格式：
1. BuildResult 内存结果对象

输出：
1. build_report.json

用法：
    from pathlib import Path
    from tools.databuilder.validation import BuildValidator

    validator = BuildValidator()
    validation_result = validator.validate(build_result, Path("data/output"))
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from .models import BuildResult, ValidationIssue, ValidationResult, ValidationSummary


class BuildValidator:
    """对构建结果执行基础校验，并输出 build_report.json。"""

    # 已知《红楼梦》清洗版应识别出 120 回。
    EXPECTED_CHAPTER_COUNT = 120

    def validate(self, build_result: BuildResult, output_dir: Path) -> ValidationResult:
        """
        执行全部校验规则，并把结果写成校验报告。

        @params:
            build_result: 已生成的章节与段落构建结果。
            output_dir: 校验报告输出目录。

        @return:
            ValidationResult 对象，包含状态、汇总、问题列表和报告路径。
        """
        issues: list[ValidationIssue] = []

        self.validate_chapter_count(build_result, issues)
        self.validate_chapter_sequence(build_result, issues)
        self.validate_duplicate_chapter_ids(build_result, issues)
        self.validate_paragraph_count(build_result, issues)
        self.validate_passage_links(build_result, issues)
        self.validate_passage_text(build_result, issues)
        self.validate_paragraph_sequence(build_result, issues)
        self.validate_suspicious_characters(build_result, issues)

        error_count = sum(1 for issue in issues if issue.level == "error")
        warning_count = sum(1 for issue in issues if issue.level == "warning")
        status = "error" if error_count > 0 else "warning" if warning_count > 0 else "ok"

        summary = ValidationSummary(
            recognized_chapter_count=len(build_result.chapters),
            passage_count=len(build_result.passages),
            error_count=error_count,
            warning_count=warning_count,
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        report_output = output_dir / "build_report.json"
        report_output.write_text(
            json.dumps(
                {
                    "status": status,
                    "summary": summary.to_dict(),
                    "issues": [issue.to_dict() for issue in issues],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        return ValidationResult(
            status=status,
            summary=summary,
            issues=issues,
            report_output=report_output,
        )

    def validate_chapter_count(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查章节总数是否符合 120 回文本预期。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        chapter_count = len(build_result.chapters)
        if chapter_count != self.EXPECTED_CHAPTER_COUNT:
            issues.append(
                ValidationIssue(
                    level="error",
                    code="CHAPTER_COUNT_MISMATCH",
                    message=f"Expected {self.EXPECTED_CHAPTER_COUNT} chapters, got {chapter_count}.",
                )
            )

    def validate_chapter_sequence(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查 chapter_no 是否从 1 开始连续递增。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        observed_numbers = [chapter.chapter_no for chapter in build_result.chapters]
        expected_numbers = list(range(1, len(build_result.chapters) + 1))

        if observed_numbers != expected_numbers:
            issues.append(
                ValidationIssue(
                    level="error",
                    code="CHAPTER_SEQUENCE_INVALID",
                    message="Chapter numbers are not continuous from 1 upward.",
                )
            )

    def validate_duplicate_chapter_ids(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查章节 ID 是否唯一。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        seen: set[str] = set()
        for chapter in build_result.chapters:
            if chapter.chapter_id in seen:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="DUPLICATE_CHAPTER_ID",
                        message=f"Duplicate chapter_id detected: {chapter.chapter_id}",
                        chapter_id=chapter.chapter_id,
                    )
                )
                continue
            seen.add(chapter.chapter_id)

    def validate_paragraph_count(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查每章是否至少切分出一个段落。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        for chapter in build_result.chapters:
            if chapter.paragraph_count <= 0:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="EMPTY_CHAPTER",
                        message="Chapter contains no paragraphs.",
                        chapter_id=chapter.chapter_id,
                    )
                )

    def validate_passage_links(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查 passage 与 chapter 的关联是否合法且数量一致。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        chapter_ids = {chapter.chapter_id for chapter in build_result.chapters}
        passages_by_chapter: dict[str, int] = {}

        for passage in build_result.passages:
            if passage.chapter_id not in chapter_ids:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="INVALID_CHAPTER_LINK",
                        message="Passage references a missing chapter_id.",
                        chapter_id=passage.chapter_id,
                        passage_id=passage.passage_id,
                    )
                )
            passages_by_chapter[passage.chapter_id] = passages_by_chapter.get(passage.chapter_id, 0) + 1

        for chapter in build_result.chapters:
            actual_count = passages_by_chapter.get(chapter.chapter_id, 0)
            if actual_count != chapter.paragraph_count:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="PARAGRAPH_COUNT_MISMATCH",
                        message=f"Chapter paragraph_count={chapter.paragraph_count}, actual passages={actual_count}.",
                        chapter_id=chapter.chapter_id,
                    )
                )

    def validate_passage_text(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查每条 passage 是否包含非空正文。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        for passage in build_result.passages:
            if not passage.text.strip():
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="EMPTY_PASSAGE",
                        message="Passage text is empty after trimming.",
                        chapter_id=passage.chapter_id,
                        passage_id=passage.passage_id,
                    )
                )

    def validate_paragraph_sequence(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查每章内部 paragraph_no 是否连续。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        grouped: dict[str, list[int]] = {}
        for passage in build_result.passages:
            grouped.setdefault(passage.chapter_id, []).append(passage.paragraph_no)

        for chapter_id, paragraph_numbers in grouped.items():
            expected_numbers = list(range(1, len(paragraph_numbers) + 1))
            if paragraph_numbers != expected_numbers:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="PARAGRAPH_SEQUENCE_INVALID",
                        message="Paragraph numbers are not continuous inside the chapter.",
                        chapter_id=chapter_id,
                    )
                )

    def validate_suspicious_characters(self, build_result: BuildResult, issues: list[ValidationIssue]) -> None:
        """
        检查文本中是否存在可疑字符，并按 passage 维度记录告警。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        for passage in build_result.passages:
            suspicious = self.find_suspicious_characters(passage.text)
            if not suspicious:
                continue

            issues.append(
                ValidationIssue(
                    level="warning",
                    code="SUSPICIOUS_CHAR",
                    message=f"Passage contains suspicious characters: {', '.join(suspicious)}",
                    chapter_id=passage.chapter_id,
                    passage_id=passage.passage_id,
                )
            )

    def find_suspicious_characters(self, text: str) -> list[str]:
        """
        返回一段文本中命中的可疑字符列表。

        @params:
            text: 待检查的正文文本。

        @return:
            命中的可疑字符列表，去重后返回。
        """
        found: list[str] = []
        for ch in text:
            if self.is_suspicious_character(ch) and ch not in found:
                found.append(ch)
        return found

    @staticmethod
    def is_suspicious_character(ch: str) -> bool:
        """
        判断一个字符是否应被视为可疑字符。

        @params:
            ch: 待判断字符。

        @return:
            若字符属于可疑字符则返回 True，否则返回 False。
        """
        if ch in {"?", "\ufffd"}:
            return True
        return unicodedata.category(ch) == "Co"
