"""
《红楼梦》数据构建回归测试

用法：
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

# 项目根目录，用于定位 data/input 下的固定测试输入。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 将项目根目录加入导入路径，保证测试运行和 IDE 解析都能定位到 tools/ 包。
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

RedMansionCorpusBuilder = import_module("tools.databuilder.builder").RedMansionCorpusBuilder
BuildValidator = import_module("tools.databuilder.validation").BuildValidator
# 默认测试输入目录，存放清洗后的主文本和参考报告。
INPUT_DIR = PROJECT_ROOT / "data" / "input"
# 默认测试输入文件，当前集成测试直接基于项目内清洗版文本执行。
INPUT_FILE = INPUT_DIR / "StoneStory.txt"


class DataBuilderIntegrationTest(unittest.TestCase):
    """验证数据构建与校验流程的核心回归结果。"""

    @classmethod
    def setUpClass(cls) -> None:
        """
        执行一次完整构建，供全部测试复用。

        @params:
            无。

        @return:
            None。
        """
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.output_dir = Path(cls.temp_dir.name)
        cls.builder = RedMansionCorpusBuilder()
        cls.validator = BuildValidator()
        cls.build_result = cls.builder.build(INPUT_FILE, cls.output_dir)
        cls.validation_result = cls.validator.validate(cls.build_result, cls.output_dir, INPUT_DIR)
        cls.report = json.loads(cls.validation_result.report_output.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        """
        清理测试过程中生成的临时输出目录。

        @params:
            无。

        @return:
            None。
        """
        cls.temp_dir.cleanup()

    def test_build_outputs_expected_counts(self) -> None:
        """
        验证章节数、段落数以及输出文件均符合当前基线。

        @params:
            无。

        @return:
            None。
        """
        self.assertEqual(120, len(self.build_result.chapters))
        self.assertEqual(3028, len(self.build_result.passages))
        self.assertTrue(self.build_result.chapters_output.exists())
        self.assertTrue(self.build_result.passages_output.exists())

    def test_validation_summary_matches_reference(self) -> None:
        """
        验证校验汇总中的关键统计值与当前参考基线一致。

        @params:
            无。

        @return:
            None。
        """
        summary = self.report["summary"]
        self.assertEqual("warning", self.validation_result.status)
        self.assertEqual(0, summary["error_count"])
        self.assertEqual(39, summary["warning_count"])
        self.assertEqual(120, summary["recognized_chapter_count"])
        self.assertEqual(3028, summary["passage_count"])
        self.assertEqual(39, summary["current_question_mark_count"])
        self.assertEqual(39, summary["reference_question_mark_count"])
        self.assertEqual(0, summary["current_private_use_count"])

    def test_report_contains_character_level_suspicious_issue(self) -> None:
        """
        验证异常字符告警已经细化到字符级定位字段。

        @params:
            无。

        @return:
            None。
        """
        suspicious_issues = [issue for issue in self.report["issues"] if issue["code"] == "SUSPICIOUS_CHAR"]
        self.assertEqual(39, len(suspicious_issues))

        title_issue = next(issue for issue in suspicious_issues if issue["source_field"] == "title")
        text_issue = next(issue for issue in suspicious_issues if issue["source_field"] == "text")

        self.assertIn("text_offset", title_issue)
        self.assertIn("suspicious_char", title_issue)
        self.assertIn("context", title_issue)
        self.assertEqual("?", title_issue["suspicious_char"])
        self.assertIsInstance(title_issue["text_offset"], int)
        self.assertTrue(title_issue["context"])

        self.assertIn("passage_id", text_issue)
        self.assertEqual("text", text_issue["source_field"])
        self.assertEqual("?", text_issue["suspicious_char"])

    def test_chapters_json_and_passages_jsonl_are_consistent(self) -> None:
        """
        验证落盘后的 chapters.json 和 passages.jsonl 条目数量与内存结果一致。

        @params:
            无。

        @return:
            None。
        """
        chapters = json.loads(self.build_result.chapters_output.read_text(encoding="utf-8"))
        passages = [
            json.loads(line)
            for line in self.build_result.passages_output.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        self.assertEqual(len(self.build_result.chapters), len(chapters))
        self.assertEqual(len(self.build_result.passages), len(passages))
        self.assertEqual("chapter_001", chapters[0]["chapter_id"])
        self.assertEqual("chapter_120", chapters[-1]["chapter_id"])
        self.assertEqual("passage_000001", passages[0]["passage_id"])


if __name__ == "__main__":
    unittest.main()
