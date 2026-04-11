"""
人物对话第一阶段测试

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

CharacterChatPromptBuilder = import_module("tools.characterchat.prompt_builder").CharacterChatPromptBuilder
CharacterChatRetriever = import_module("tools.characterchat.retriever").CharacterChatRetriever


class CharacterChatTest(unittest.TestCase):
    """验证人物对话第一阶段的检索和 prompt payload 生成。"""

    def setUp(self) -> None:
        """
        创建最小人物 skill 测试目录和证据文件。

        @params:
            无。

        @return:
            None。
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.skill_root = self.root / "skill" / "characters"
        self.skill_dir = self.skill_root / "jia-baoyu.skill"
        self.skill_dir.mkdir(parents=True)

        (self.skill_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "id": "jia-baoyu",
                    "name": "贾宝玉",
                    "aliases": ["宝玉", "宝二爷"],
                    "retrieval_hint": {"character_keywords": ["贾宝玉", "宝玉", "黛玉", "功名"]},
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.skill_dir / "persona.md").write_text("# Persona\n\n宝玉人物说明。", encoding="utf-8")
        (self.skill_dir / "style.md").write_text("# Style\n\n宝玉风格说明。", encoding="utf-8")
        (self.skill_dir / "boundaries.md").write_text("# Boundaries\n\n不要脱离原著。", encoding="utf-8")
        (self.skill_dir / "relations.md").write_text(
            "# Relations\n\n- `林黛玉` -- `friend`（朋友）--> `贾宝玉`\n- `贾宝玉` -- `son`（子）--> `贾政`\n",
            encoding="utf-8",
        )
        (self.skill_dir / "source_report.json").write_text(
            json.dumps({"character_id": "jia-baoyu", "character_name": "贾宝玉"}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.skill_dir / "style_evidence.jsonl").write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "character_id": "jia-baoyu",
                            "character_name": "贾宝玉",
                            "chapter_id": "chapter_003",
                            "passage_id": "passage_000101",
                            "paragraph_id": "chapter_003_paragraph_010",
                            "paragraph_no": 10,
                            "matched_terms": ["宝玉", "黛玉"],
                            "score": 9,
                            "signal_type": "speech_marker",
                            "signals": ["contains_speech_marker"],
                            "text": "宝玉道：“林妹妹来了，我心里欢喜。”",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "character_id": "jia-baoyu",
                            "character_name": "贾宝玉",
                            "chapter_id": "chapter_010",
                            "passage_id": "passage_000300",
                            "paragraph_id": "chapter_010_paragraph_005",
                            "paragraph_no": 5,
                            "matched_terms": ["宝玉", "功名"],
                            "score": 6,
                            "signal_type": "named_dialogue_context",
                            "signals": ["contains_dialogue_quotes"],
                            "text": "众人说起功名，宝玉只是摇头不答。",
                        },
                        ensure_ascii=False,
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (self.skill_dir / "evidence_ranked.jsonl").write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "character_id": "jia-baoyu",
                            "character_name": "贾宝玉",
                            "chapter_id": "chapter_003",
                            "passage_id": "passage_000101",
                            "paragraph_id": "chapter_003_paragraph_010",
                            "paragraph_no": 10,
                            "matched_terms": ["宝玉", "黛玉"],
                            "score": 9,
                            "signals": ["contains_speech_marker"],
                            "noise_flags": [],
                            "text": "宝玉道：“林妹妹来了，我心里欢喜。”",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "character_id": "jia-baoyu",
                            "character_name": "贾宝玉",
                            "chapter_id": "chapter_010",
                            "passage_id": "passage_000300",
                            "paragraph_id": "chapter_010_paragraph_005",
                            "paragraph_no": 5,
                            "matched_terms": ["宝玉", "功名"],
                            "score": 6,
                            "signals": ["contains_dialogue_quotes"],
                            "noise_flags": [],
                            "text": "众人说起功名，宝玉只是摇头不答。",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "character_id": "jia-baoyu",
                            "character_name": "贾宝玉",
                            "chapter_id": "chapter_006",
                            "passage_id": "passage_000210",
                            "paragraph_id": "chapter_006_paragraph_003",
                            "paragraph_no": 3,
                            "matched_terms": ["宝玉"],
                            "score": 2,
                            "signals": ["contains_alias"],
                            "noise_flags": ["short_alias_only"],
                            "text": "宝玉在房中坐着，并未答话。",
                        },
                        ensure_ascii=False,
                    ),
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        """
        清理测试临时目录。

        @params:
            无。

        @return:
            None。
        """
        self.temp_dir.cleanup()

    def test_retriever_returns_ranked_context(self) -> None:
        """
        验证检索器会返回人物资产、关系和分层证据。

        @params:
            无。

        @return:
            None。
        """
        retriever = CharacterChatRetriever()
        result = retriever.retrieve(self.skill_root, "jia-baoyu", "你怎么看黛玉和功名？", style_top_k=2, fact_top_k=2)

        self.assertEqual("贾宝玉", result["character"]["name"])
        self.assertIn("黛玉", result["query_terms"])
        self.assertIn("功名", result["query_terms"])
        self.assertEqual(2, len(result["retrieval"]["style_evidence"]))
        self.assertEqual(1, len(result["retrieval"]["relations"]))
        self.assertEqual("passage_000101", result["retrieval"]["style_evidence"][0]["passage_id"])

    def test_prompt_builder_generates_messages(self) -> None:
        """
        验证 prompt builder 会输出 messages 数组和上下文。

        @params:
            无。

        @return:
            None。
        """
        retriever = CharacterChatRetriever()
        prompt_builder = CharacterChatPromptBuilder()

        retrieval_result = retriever.retrieve(self.skill_root, "jia-baoyu", "你怎么看黛玉？", style_top_k=1, fact_top_k=1)
        payload = prompt_builder.build_prompt_payload(retrieval_result)

        self.assertEqual(2, len(payload["messages"]))
        self.assertEqual("system", payload["messages"][0]["role"])
        self.assertEqual("user", payload["messages"][1]["role"])
        self.assertIn("贾宝玉", payload["messages"][0]["content"])
        self.assertIn("你怎么看黛玉？", payload["messages"][1]["content"])
        self.assertEqual(1, len(payload["context"]["retrieval"]["style_evidence"]))


if __name__ == "__main__":
    unittest.main()
