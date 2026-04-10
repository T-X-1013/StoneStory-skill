"""
《红楼梦》章节与段落构建器

支持格式：
1. .txt 文件（UTF-8 编码的清洗版《红楼梦》全文）

输出：
1. chapters.json
2. passages.jsonl

用法：
    from pathlib import Path
    from tools.databuilder.builder import RedMansionCorpusBuilder

    builder = RedMansionCorpusBuilder()
    result = builder.build(
        input_file=Path("data/input/StoneStory.txt"),
        output_dir=Path("data/output"),
    )
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .models import BuildResult, Chapter, Passage


class RedMansionCorpusBuilder:
    """将清洗版 txt 文本构建为章节级和段落级结构化数据。"""

    # 章节标题识别正则，匹配“第...回 标题正文”格式。
    CHAPTER_TITLE_PATTERN = re.compile(r"^(第[〇零一二三四五六七八九十百千万两]+回)\s+(.+)$")

    def build(self, input_file: Path, output_dir: Path) -> BuildResult:
        """
        读取原始文本，完成切章切段，并把结果写到输出目录。

        @params:
            input_file: 输入 txt 文件路径，要求为 UTF-8 编码的清洗文本。
            output_dir: 输出目录，生成 chapters.json 和 passages.jsonl。

        @return:
            BuildResult 对象，包含内存中的 chapters/passages 以及输出文件路径。
        """
        source_lines = input_file.read_text(encoding="utf-8").splitlines()
        chapters: list[Chapter] = []
        passages: list[Passage] = []
        current_body_lines: list[str] = []

        current_label: str | None = None
        current_title: str | None = None
        current_chapter_no = 0
        passage_counter = 0

        for source_line in source_lines:
            cleaned_line = self.remove_bom(source_line)
            matcher = self.CHAPTER_TITLE_PATTERN.match(self.normalize_chapter_line(cleaned_line))
            if matcher:
                # 遇到新章标题时，先把上一章缓存的正文收束成结构化结果。
                if current_label is not None and current_title is not None:
                    passage_counter = self.flush_chapter(
                        chapters=chapters,
                        passages=passages,
                        chapter_no=current_chapter_no,
                        chapter_label=current_label,
                        title=current_title,
                        body_lines=current_body_lines,
                        passage_counter=passage_counter,
                    )
                    current_body_lines.clear()

                # 标题行本身不进入正文，只更新当前章节元信息。
                current_label = matcher.group(1)
                current_title = matcher.group(2)
                current_chapter_no = self.parse_chapter_number(current_label)
                continue

            # 第一章标题之前的书名、作者等前置内容会被自然忽略。
            if current_label is not None:
                current_body_lines.append(cleaned_line)

        # 最后一章不会再遇到“下一章标题”，因此文件结束后需要手动收尾。
        if current_label is not None and current_title is not None:
            self.flush_chapter(
                chapters=chapters,
                passages=passages,
                chapter_no=current_chapter_no,
                chapter_label=current_label,
                title=current_title,
                body_lines=current_body_lines,
                passage_counter=passage_counter,
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        chapters_output = output_dir / "chapters.json"
        passages_output = output_dir / "passages.jsonl"

        chapters_output.write_text(
            json.dumps([chapter.to_dict() for chapter in chapters], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        passages_output.write_text(
            "\n".join(json.dumps(passage.to_dict(), ensure_ascii=False) for passage in passages) + "\n",
            encoding="utf-8",
        )

        return BuildResult(
            chapters=chapters,
            passages=passages,
            chapters_output=chapters_output,
            passages_output=passages_output,
        )

    def flush_chapter(
        self,
        *,
        chapters: list[Chapter],
        passages: list[Passage],
        chapter_no: int,
        chapter_label: str,
        title: str,
        body_lines: list[str],
        passage_counter: int,
    ) -> int:
        """
        将当前缓存的一整章正文转换为章节对象和段落对象。

        @params:
            chapters: 章节结果集合，会被追加写入新的 Chapter。
            passages: 段落结果集合，会被追加写入新的 Passage。
            chapter_no: 当前章节的数字序号。
            chapter_label: 当前章节的原始章回编号文本。
            title: 当前章节标题正文。
            body_lines: 当前章节累计的正文行列表。
            passage_counter: 当前全局段落计数器。

        @return:
            更新后的全局段落计数器。
        """
        chapter_id = f"chapter_{chapter_no:03d}"
        paragraphs = self.split_paragraphs(body_lines)
        chapter_body = "\n\n".join(paragraphs)

        # 先生成章节级元信息，供 chapters.json 使用。
        chapters.append(
            Chapter(
                chapter_id=chapter_id,
                chapter_no=chapter_no,
                chapter_label=chapter_label,
                title=title,
                paragraph_count=len(paragraphs),
                source_text_length=len(chapter_body),
            )
        )

        # 再为该章节中的每个段落生成稳定的 passage 标识。
        for index, paragraph_text in enumerate(paragraphs, start=1):
            passage_counter += 1
            passages.append(
                Passage(
                    passage_id=f"passage_{passage_counter:06d}",
                    chapter_id=chapter_id,
                    paragraph_id=f"{chapter_id}_paragraph_{index:03d}",
                    paragraph_no=index,
                    text=paragraph_text,
                )
            )

        return passage_counter

    def split_paragraphs(self, body_lines: list[str]) -> list[str]:
        """
        按空行把单章正文切分为段落列表。

        @params:
            body_lines: 单章正文的原始文本行列表。

        @return:
            段落文本列表，每个元素对应一个 passage 的正文。
        """
        paragraphs: list[str] = []
        current_paragraph: list[str] = []

        for line in body_lines:
            if self.is_blank(line):
                # 空行被视为当前段落的边界。
                self.flush_paragraph(paragraphs, current_paragraph)
                continue
            current_paragraph.append(self.trim_line(line))

        self.flush_paragraph(paragraphs, current_paragraph)
        return paragraphs

    @staticmethod
    def flush_paragraph(paragraphs: list[str], current_paragraph: list[str]) -> None:
        """
        把当前段落缓存收束为一个完整段落。

        @params:
            paragraphs: 最终段落集合。
            current_paragraph: 当前正在累计的段落行列表。

        @return:
            None。
        """
        if not current_paragraph:
            return

        # 段内保留换行，便于保留诗词、对联等多行文本结构。
        paragraphs.append("\n".join(current_paragraph))
        current_paragraph.clear()

    def is_blank(self, line: str) -> bool:
        """
        判断一行在修剪空白后是否为空。

        @params:
            line: 原始文本行。

        @return:
            若该行视为空行则返回 True，否则返回 False。
        """
        return self.trim_line(line) == ""

    def trim_line(self, line: str) -> str:
        """
        去除一行首尾的各种空白字符。

        @params:
            line: 原始文本行。

        @return:
            去除首尾空白后的文本。
        """
        start = 0
        end = len(line)

        while start < end and self.is_whitespace_like(line[start]):
            start += 1
        while end > start and self.is_whitespace_like(line[end - 1]):
            end -= 1

        return line[start:end]

    @staticmethod
    def is_whitespace_like(ch: str) -> bool:
        """
        判断字符是否应被视为空白，包括全角空格和不间断空格。

        @params:
            ch: 待判断字符。

        @return:
            若字符应被视为空白则返回 True，否则返回 False。
        """
        return ch.isspace() or ch in {"\u3000", "\u00A0"}

    def normalize_chapter_line(self, line: str) -> str:
        """
        标准化标题行中的连续空白，降低排版差异带来的识别误差。

        @params:
            line: 原始标题行文本。

        @return:
            空白标准化后的标题行文本。
        """
        builder: list[str] = []
        previous_whitespace = False

        for current in line:
            if self.is_whitespace_like(current):
                if not previous_whitespace:
                    builder.append(" ")
                    previous_whitespace = True
            else:
                builder.append(current)
                previous_whitespace = False

        return "".join(builder).strip()

    @staticmethod
    def remove_bom(line: str) -> str:
        """
        去除文本开头可能存在的 UTF-8 BOM。

        @params:
            line: 原始文本行。

        @return:
            去除 BOM 后的文本行。
        """
        if line.startswith("\ufeff"):
            return line[1:]
        return line

    def parse_chapter_number(self, chapter_label: str) -> int:
        """
        把“第一回”这类章回编号文本解析为阿拉伯数字。

        @params:
            chapter_label: 原始章回编号文本。

        @return:
            对应的章节数字序号。
        """
        numeric_part = chapter_label[1:-1]
        return self.parse_chinese_number(numeric_part)

    def parse_chinese_number(self, value: str) -> int:
        """
        将中文数字串转换为整数章节号。

        @params:
            value: 中文数字文本，例如“一百二十”。

        @return:
            对应的整数值。
        """
        digits = self.chinese_digits()
        result = 0
        current = 0

        for ch in value:
            if ch in digits:
                current = digits[ch]
                continue

            unit = {
                "十": 10,
                "百": 100,
                "千": 1000,
                "万": 10000,
            }.get(ch)

            if unit is None:
                raise ValueError(f"Unsupported chapter number: {value}")

            if current == 0:
                current = 1

            # 遇到“十、百、千、万”时，将前一个数字与单位组合后累计。
            result += current * unit
            current = 0

        return result + current

    @staticmethod
    def chinese_digits() -> dict[str, int]:
        """
        返回当前支持的中文数字到整数的映射表。

        @params:
            无。

        @return:
            中文数字到整数的映射字典。
        """
        return {
            "零": 0,
            "〇": 0,
            "一": 1,
            "二": 2,
            "两": 2,
            "三": 3,
            "四": 4,
            "五": 5,
            "六": 6,
            "七": 7,
            "八": 8,
            "九": 9,
        }
