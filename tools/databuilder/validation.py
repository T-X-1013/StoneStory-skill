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

    def validate(self, build_result: BuildResult, output_dir: Path, input_dir: Path | None = None) -> ValidationResult:
        """
        执行全部校验规则，并把结果写成校验报告。

        @params:
            build_result: 已生成的章节与段落构建结果。
            output_dir: 校验报告输出目录。
            input_dir: 输入目录；若存在参考报告文件，会一并参与校验。

        @return:
            ValidationResult 对象，包含状态、汇总、问题列表和报告路径。
        """
        issues: list[ValidationIssue] = []
        reference_quality_report = self.load_json(input_dir / "quality_report.json") if input_dir else None
        reference_chapters = self.load_json(input_dir / "chapters_detected.json") if input_dir else None
        reference_suspicious_report = self.load_json(input_dir / "suspicious_char_report.json") if input_dir else None

        self.validate_chapter_count(build_result, issues)
        self.validate_chapter_sequence(build_result, issues)
        self.validate_duplicate_chapter_ids(build_result, issues)
        self.validate_paragraph_count(build_result, issues)
        self.validate_passage_links(build_result, issues)
        self.validate_passage_text(build_result, issues)
        self.validate_paragraph_sequence(build_result, issues)
        self.validate_suspicious_characters(build_result, issues)
        self.validate_quality_report_alignment(build_result, reference_quality_report, issues)
        self.validate_chapter_reference_alignment(build_result, reference_chapters, issues)
        question_mark_count, private_use_count = self.count_suspicious_characters_in_outputs(build_result)
        self.validate_suspicious_report_alignment(
            question_mark_count,
            private_use_count,
            reference_suspicious_report,
            issues,
        )

        error_count = sum(1 for issue in issues if issue.level == "error")
        warning_count = sum(1 for issue in issues if issue.level == "warning")
        status = "error" if error_count > 0 else "warning" if warning_count > 0 else "ok"

        summary = ValidationSummary(
            recognized_chapter_count=len(build_result.chapters),
            passage_count=len(build_result.passages),
            error_count=error_count,
            warning_count=warning_count,
            reference_chapter_count=self.read_reference_chapter_count(reference_quality_report),
            current_question_mark_count=question_mark_count,
            reference_question_mark_count=self.read_reference_question_mark_count(reference_suspicious_report),
            current_private_use_count=private_use_count,
            reference_removed_private_use_count=self.read_reference_private_use_count(reference_suspicious_report),
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

    def load_json(self, file_path: Path) -> dict | list | None:
        """
        读取一份 JSON 参考文件；文件不存在时返回 None。

        @params:
            file_path: 待读取的 JSON 文件路径。

        @return:
            解析后的 JSON 数据；若文件不存在则返回 None。
        """
        if not file_path.exists():
            return None
        return json.loads(file_path.read_text(encoding="utf-8"))

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
        检查文本中是否存在可疑字符，并按字符位置记录告警。

        @params:
            build_result: 已生成的章节与段落构建结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        for chapter in build_result.chapters:
            self.append_suspicious_character_issues(
                text=chapter.chapter_label,
                chapter_id=chapter.chapter_id,
                passage_id=None,
                source_field="chapter_label",
                issues=issues,
            )
            self.append_suspicious_character_issues(
                text=chapter.title,
                chapter_id=chapter.chapter_id,
                passage_id=None,
                source_field="title",
                issues=issues,
            )

        for passage in build_result.passages:
            self.append_suspicious_character_issues(
                text=passage.text,
                chapter_id=passage.chapter_id,
                passage_id=passage.passage_id,
                source_field="text",
                issues=issues,
            )

    def append_suspicious_character_issues(
        self,
        text: str,
        chapter_id: str | None,
        passage_id: str | None,
        source_field: str,
        issues: list[ValidationIssue],
    ) -> None:
        """
        扫描一段文本中的异常字符，并将每次命中写成独立告警。

        @params:
            text: 待扫描文本。
            chapter_id: 关联章节 ID；若无则为空。
            passage_id: 关联段落 ID；若无则为空。
            source_field: 命中来源字段名。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        for offset, ch in self.find_suspicious_occurrences(text):
            issues.append(
                ValidationIssue(
                    level="warning",
                    code="SUSPICIOUS_CHAR",
                    message=f"Suspicious character {repr(ch)} found in {source_field} at offset {offset}.",
                    chapter_id=chapter_id,
                    passage_id=passage_id,
                    source_field=source_field,
                    text_offset=offset,
                    suspicious_char=ch,
                    context=self.extract_context(text, offset),
                )
            )

    def validate_quality_report_alignment(
        self,
        build_result: BuildResult,
        reference_quality_report: dict | list | None,
        issues: list[ValidationIssue],
    ) -> None:
        """
        检查当前构建结果是否与 quality_report.json 一致。

        @params:
            build_result: 已生成的章节与段落构建结果。
            reference_quality_report: 参考质量报告内容。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        if not isinstance(reference_quality_report, dict):
            return

        reference_count = reference_quality_report.get("recognized_chapter_count")
        if isinstance(reference_count, int) and reference_count != len(build_result.chapters):
            issues.append(
                ValidationIssue(
                    level="error",
                    code="QUALITY_REPORT_COUNT_MISMATCH",
                    message=f"quality_report.json expects {reference_count} chapters, current build has {len(build_result.chapters)}.",
                )
            )

        missing_chapters = reference_quality_report.get("missing_chapters", [])
        if missing_chapters:
            issues.append(
                ValidationIssue(
                    level="error",
                    code="QUALITY_REPORT_MISSING_CHAPTERS",
                    message=f"quality_report.json reports missing chapters: {missing_chapters}.",
                )
            )

        duplicate_chapters = reference_quality_report.get("duplicate_chapters", [])
        if duplicate_chapters:
            issues.append(
                ValidationIssue(
                    level="error",
                    code="QUALITY_REPORT_DUPLICATE_CHAPTERS",
                    message=f"quality_report.json reports duplicate chapters: {duplicate_chapters}.",
                )
            )

    def validate_chapter_reference_alignment(
        self,
        build_result: BuildResult,
        reference_chapters: dict | list | None,
        issues: list[ValidationIssue],
    ) -> None:
        """
        检查当前识别出的章节标题是否与 chapters_detected.json 一致。

        @params:
            build_result: 已生成的章节与段落构建结果。
            reference_chapters: 参考章节识别结果。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        if not isinstance(reference_chapters, list):
            return

        if len(reference_chapters) != len(build_result.chapters):
            issues.append(
                ValidationIssue(
                    level="error",
                    code="CHAPTER_REFERENCE_COUNT_MISMATCH",
                    message=f"chapters_detected.json contains {len(reference_chapters)} chapters, current build has {len(build_result.chapters)}.",
                )
            )
            return

        for chapter, reference in zip(build_result.chapters, reference_chapters):
            reference_label = reference.get("chapter_label")
            reference_title = reference.get("title")

            if reference_label != chapter.chapter_label:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="CHAPTER_LABEL_MISMATCH",
                        message=f"Reference chapter_label={reference_label}, current={chapter.chapter_label}.",
                        chapter_id=chapter.chapter_id,
                    )
                )

            if reference_title != chapter.title:
                issues.append(
                    ValidationIssue(
                        level="error",
                        code="CHAPTER_TITLE_MISMATCH",
                        message=f"Reference title={reference_title}, current={chapter.title}.",
                        chapter_id=chapter.chapter_id,
                    )
                )

    def count_suspicious_characters_in_outputs(self, build_result: BuildResult) -> tuple[int, int]:
        """
        统计当前结构化结果中的问号和私有区字符数量。

        @params:
            build_result: 已生成的章节与段落构建结果。

        @return:
            二元组：(问号总数, 私有区字符总数)。
        """
        question_mark_count = 0
        private_use_count = 0

        for chapter in build_result.chapters:
            question_mark_count += chapter.chapter_label.count("?")
            question_mark_count += chapter.title.count("?")
            private_use_count += self.count_private_use_characters(chapter.chapter_label)
            private_use_count += self.count_private_use_characters(chapter.title)

        for passage in build_result.passages:
            question_mark_count += passage.text.count("?")
            private_use_count += self.count_private_use_characters(passage.text)

        return question_mark_count, private_use_count

    def count_private_use_characters(self, text: str) -> int:
        """
        统计文本中的私有区字符数量。

        @params:
            text: 待统计文本。

        @return:
            私有区字符数量。
        """
        return sum(1 for ch in text if unicodedata.category(ch) == "Co")

    def validate_suspicious_report_alignment(
        self,
        question_mark_count: int,
        private_use_count: int,
        reference_suspicious_report: dict | list | None,
        issues: list[ValidationIssue],
    ) -> None:
        """
        检查当前异常字符统计是否与 suspicious_char_report.json 一致。

        @params:
            question_mark_count: 当前结构化结果中的问号总数。
            private_use_count: 当前结构化结果中的私有区字符总数。
            reference_suspicious_report: 参考异常字符报告内容。
            issues: 校验问题集合，用于追加写入问题。

        @return:
            None。
        """
        if not isinstance(reference_suspicious_report, dict):
            return

        reference_question_marks = reference_suspicious_report.get("total_question_marks")
        if isinstance(reference_question_marks, int) and reference_question_marks != question_mark_count:
            issues.append(
                ValidationIssue(
                    level="warning",
                    code="QUESTION_MARK_COUNT_MISMATCH",
                    message=f"suspicious_char_report.json expects {reference_question_marks} question marks, current structured outputs contain {question_mark_count}.",
                )
            )

        if private_use_count > 0:
            issues.append(
                ValidationIssue(
                    level="warning",
                    code="PRIVATE_USE_CHAR_REMAINING",
                    message=f"Structured outputs still contain {private_use_count} private-use characters.",
                )
            )

    def find_suspicious_occurrences(self, text: str) -> list[tuple[int, str]]:
        """
        返回一段文本中命中的可疑字符及其字符偏移。

        @params:
            text: 待检查的正文文本。

        @return:
            命中的可疑字符位置列表，每项为 (字符偏移, 字符本身)。
        """
        return [(index, ch) for index, ch in enumerate(text) if self.is_suspicious_character(ch)]

    def extract_context(self, text: str, offset: int, radius: int = 15) -> str:
        """
        提取命中位置附近的上下文片段，便于人工核对。

        @params:
            text: 原始文本。
            offset: 命中的字符偏移。
            radius: 命中位置两侧保留的字符数。

        @return:
            截取后的上下文片段。
        """
        start = max(0, offset - radius)
        end = min(len(text), offset + radius + 1)
        return text[start:end]

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

    def read_reference_chapter_count(self, reference_quality_report: dict | list | None) -> int | None:
        """
        从参考质量报告中读取章节数。

        @params:
            reference_quality_report: 参考质量报告内容。

        @return:
            参考章节数；若不可用则返回 None。
        """
        if not isinstance(reference_quality_report, dict):
            return None
        value = reference_quality_report.get("recognized_chapter_count")
        return value if isinstance(value, int) else None

    def read_reference_question_mark_count(self, reference_suspicious_report: dict | list | None) -> int | None:
        """
        从参考异常报告中读取问号总数。

        @params:
            reference_suspicious_report: 参考异常字符报告内容。

        @return:
            参考问号总数；若不可用则返回 None。
        """
        if not isinstance(reference_suspicious_report, dict):
            return None
        value = reference_suspicious_report.get("total_question_marks")
        return value if isinstance(value, int) else None

    def read_reference_private_use_count(self, reference_suspicious_report: dict | list | None) -> int | None:
        """
        从参考异常报告中读取已清理的私有区字符数量。

        @params:
            reference_suspicious_report: 参考异常字符报告内容。

        @return:
            参考报告中的私有区字符数量；若不可用则返回 None。
        """
        if not isinstance(reference_suspicious_report, dict):
            return None
        value = reference_suspicious_report.get("removed_private_use_char_count")
        return value if isinstance(value, int) else None
