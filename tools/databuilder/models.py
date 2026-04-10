"""
《红楼梦》数据模型定义

支持格式：
1. Python dataclass 数据结构

输出：
1. 章节模型
2. 段落模型
3. 构建结果模型
4. 校验报告模型

用法：
    from tools.databuilder.models import Chapter, Passage, BuildResult
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Chapter:
    """章节级输出模型，对应 chapters.json 中的一个对象。"""

    chapter_id: str         # 章节唯一 ID，例如 chapter_001。
    chapter_no: int         # 章节数字序号，例如 1、20、120。
    chapter_label: str      # 原始章回编号文本，例如“第一回”。
    title: str              # 章回标题正文，不包含“第...回”部分。
    paragraph_count: int    # 当前章节切分出的段落数量。
    source_text_length: int # 当前章节正文清理空白后的字符长度。

    def to_dict(self) -> dict[str, object]:
        """
        将章节对象转换为可直接写入 JSON 的字典结构。

        @params:
            无。

        @return:
            包含 chapter 字段的字典对象。
        """
        return {
            "chapter_id": self.chapter_id,
            "chapter_no": self.chapter_no,
            "chapter_label": self.chapter_label,
            "title": self.title,
            "paragraph_count": self.paragraph_count,
            "source_text_length": self.source_text_length,
        }


@dataclass(frozen=True)
class Passage:
    """段落级输出模型，对应 passages.jsonl 中的一行对象。"""

    passage_id: str    # 全书范围内唯一的段落 ID。
    chapter_id: str    # 当前段落所属章节 ID。
    paragraph_id: str  # 当前段落在章内的定位 ID。
    paragraph_no: int  # 当前段落在所属章节中的顺序号。
    text: str          # 当前段落的正文内容。

    def to_dict(self) -> dict[str, object]:
        """
        将段落对象转换为可直接写入 JSON 的字典结构。

        @params:
            无。

        @return:
            包含 passage 字段的字典对象。
        """
        return {
            "passage_id": self.passage_id,
            "chapter_id": self.chapter_id,
            "paragraph_id": self.paragraph_id,
            "paragraph_no": self.paragraph_no,
            "text": self.text,
        }


@dataclass(frozen=True)
class BuildResult:
    """封装一次数据构建的内存结果与输出文件路径。"""

    chapters: list[Chapter]  # 本次构建生成的全部章节对象。
    passages: list[Passage]  # 本次构建生成的全部段落对象。
    chapters_output: Path    # chapters.json 的输出路径。
    passages_output: Path    # passages.jsonl 的输出路径。


@dataclass(frozen=True)
class ValidationIssue:
    """表示一次校验中发现的一条具体问题。"""

    level: str                          # 问题级别，例如 error 或 warning。
    code: str                           # 问题代码，便于后续按类型筛选。
    message: str                        # 面向人类阅读的问题说明。
    chapter_id: str | None = None       # 关联章节 ID；若无则为空。
    passage_id: str | None = None       # 关联段落 ID；若无则为空。
    source_field: str | None = None     # 命中异常字符的字段名，例如 title 或 text。
    text_offset: int | None = None      # 异常字符在字段文本中的字符偏移，从 0 开始。
    suspicious_char: str | None = None  # 命中的异常字符本身。
    context: str | None = None          # 命中位置附近的上下文片段。

    def to_dict(self) -> dict[str, object]:
        """
        将校验问题对象转换为可直接写入 JSON 的字典结构。

        @params:
            无。

        @return:
            包含校验问题字段的字典对象。
        """
        data: dict[str, object] = {
            "level": self.level,
            "code": self.code,
            "message": self.message,
        }
        if self.chapter_id is not None:
            data["chapter_id"] = self.chapter_id
        if self.passage_id is not None:
            data["passage_id"] = self.passage_id
        if self.source_field is not None:
            data["source_field"] = self.source_field
        if self.text_offset is not None:
            data["text_offset"] = self.text_offset
        if self.suspicious_char is not None:
            data["suspicious_char"] = self.suspicious_char
        if self.context is not None:
            data["context"] = self.context
        return data


@dataclass(frozen=True)
class ValidationSummary:
    """表示一次校验任务的汇总统计信息。"""

    recognized_chapter_count: int                    # 本次识别出的章节数量。
    passage_count: int                               # 本次生成的段落数量。
    error_count: int                                 # error 级问题数量。
    warning_count: int                               # warning 级问题数量。
    reference_chapter_count: int | None = None       # 参考质量报告中的章节数量。
    current_question_mark_count: int | None = None   # 当前结构化结果中的问号数量。
    reference_question_mark_count: int | None = None # 参考异常报告中的问号数量。
    current_private_use_count: int | None = None     # 当前结构化结果中的私有区字符数量。
    reference_removed_private_use_count: int | None = None # 参考报告中已清理的私有区字符数量。

    def to_dict(self) -> dict[str, object]:
        """
        将校验汇总对象转换为可直接写入 JSON 的字典结构。

        @params:
            无。

        @return:
            包含校验汇总字段的字典对象。
        """
        return {
            "recognized_chapter_count": self.recognized_chapter_count,
            "passage_count": self.passage_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "reference_chapter_count": self.reference_chapter_count,
            "current_question_mark_count": self.current_question_mark_count,
            "reference_question_mark_count": self.reference_question_mark_count,
            "current_private_use_count": self.current_private_use_count,
            "reference_removed_private_use_count": self.reference_removed_private_use_count,
        }


@dataclass(frozen=True)
class ValidationResult:
    """表示一次校验任务的最终结果与报告路径。"""

    status: str                    # 整体状态：ok、warning 或 error。
    summary: ValidationSummary     # 本次校验的汇总统计。
    issues: list[ValidationIssue]  # 本次校验发现的全部问题。
    report_output: Path            # build_report.json 的输出路径。

    def to_dict(self) -> dict[str, object]:
        """
        将完整校验结果转换为可直接写入 JSON 的字典结构。

        @params:
            无。

        @return:
            包含状态、汇总和问题列表的字典对象。
        """
        return {
            "status": self.status,
            "summary": self.summary.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
        }
