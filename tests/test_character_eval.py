"""
人物对话评估测试

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


# 项目根目录，用于定位 tools/ 包。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
# 将项目根目录加入导入路径，保证测试运行和 IDE 解析都能定位到 tools/ 包。
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

CharacterChatEvaluator = import_module("tools.charactereval.evaluator").CharacterChatEvaluator


class CharacterChatEvalTest(unittest.TestCase):
    """验证人物对话第四阶段的评估报告生成。"""

    def setUp(self) -> None:
        """
        创建最小 prompt payload 和回答文件。

        @params:
            无。

        @return:
            None。
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.payload_file = self.root / "jia-baoyu_prompt_payload.json"
        self.response_json = self.root / "response.json"
        self.response_txt = self.root / "response.txt"

        payload = {
            "character": {"id": "jia-baoyu", "name": "贾宝玉", "aliases": ["宝玉"], "skill_dir": "skill/characters/jia-baoyu.skill"},
            "user_query": "你怎么看黛玉？",
            "query_terms": ["黛玉"],
            "messages": [],
            "context": {
                "constraints": {},
                "retrieval": {
                    "relations": [],
                    "style_evidence": [
                        {
                            "chapter_id": "chapter_064",
                            "passage_id": "passage_001716",
                            "text": "宝玉道：“妹妹这两天可大好些了？”",
                        }
                    ],
                    "fact_evidence": [
                        {
                            "chapter_id": "chapter_030",
                            "passage_id": "passage_000853",
                            "text": "话说林黛玉与宝玉角口后，也自后悔。",
                        }
                    ],
                },
            },
        }
        self.payload_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        self.response_json.write_text(
            json.dumps(
                {
                    "assistant_response": "黛玉妹妹自然是极好的人，我岂敢轻慢。[passage_001716]",
                    "cited_passage_ids": ["passage_001716"],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        self.response_txt.write_text("哈哈，这事我一时也不好说。[passage_999999]", encoding="utf-8")

    def tearDown(self) -> None:
        """
        清理测试临时目录。

        @params:
            无。

        @return:
            None。
        """
        self.temp_dir.cleanup()

    def test_evaluate_from_json_response_builds_manual_rubric(self) -> None:
        """
        验证 JSON 回答输入会生成自动检查结果和人工评分表。

        @params:
            无。

        @return:
            None。
        """
        evaluator = CharacterChatEvaluator()
        report = evaluator.evaluate_from_files(self.payload_file, response_file=self.response_json)
        report_dict = report.to_dict()

        self.assertEqual("pending_manual_review", report.status)
        self.assertEqual("jia-baoyu", report.character_id)
        self.assertIn("黛玉", report.auto_checks["query_term_hits"])
        self.assertEqual(["passage_001716"], report.auto_checks["valid_citations"])
        self.assertEqual([], report.auto_checks["invalid_citations"])
        self.assertIn("in_character", report_dict["manual_rubric"])
        self.assertEqual("1-5", report_dict["manual_rubric"]["grounded_in_evidence"]["scale"])

    def test_evaluate_from_text_response_flags_modern_and_invalid_citation(self) -> None:
        """
        验证纯文本回答输入会命中现代表达风险和无效证据引用。

        @params:
            无。

        @return:
            None。
        """
        evaluator = CharacterChatEvaluator()
        report = evaluator.evaluate_from_files(self.payload_file, response_file=self.response_txt)

        self.assertIn("哈哈", report.auto_checks["modern_expression_hits"])
        self.assertEqual(["passage_999999"], report.auto_checks["invalid_citations"])
        self.assertEqual([], report.auto_checks["valid_citations"])


if __name__ == "__main__":
    unittest.main()
