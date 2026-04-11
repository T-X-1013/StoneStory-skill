"""
人物 skill 生成器测试

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

CharacterSkillBuilder = import_module("tools.characterskill.builder").CharacterSkillBuilder


class CharacterSkillBuilderTest(unittest.TestCase):
    """验证人物 skill 第一版生成器的核心行为。"""

    def setUp(self) -> None:
        """
        创建临时目录，并写入最小测试数据。

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
                    "aliases": ["宝玉"],
                    "evidence_terms": ["贾宝玉", "宝玉"],
                    "exclude_terms": ["通灵宝玉", "甄宝玉"],
                    "retrieval_hint": {"character_keywords": ["贾宝玉", "宝玉"]},
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        self.triples_file = self.root / "data" / "input" / "triples.csv"
        self.triples_file.parent.mkdir(parents=True)
        self.triples_file.write_text(
            "head,tail,relation,label\n"
            "贾宝玉,贾政,son,子\n"
            "袭人,贾宝玉,servant_girl,丫鬟\n"
            "林黛玉,林如海,daughter,女\n",
            encoding="utf-8",
        )

        self.passages_file = self.root / "data" / "output" / "passages.jsonl"
        self.passages_file.parent.mkdir(parents=True)
        self.passages_file.write_text(
            "\n".join(
                [
                    json.dumps(
                        {
                            "passage_id": "passage_000001",
                            "chapter_id": "chapter_001",
                            "paragraph_id": "chapter_001_paragraph_001",
                            "paragraph_no": 1,
                            "text": "通灵宝玉原是仙物。",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "passage_id": "passage_000002",
                            "chapter_id": "chapter_001",
                            "paragraph_id": "chapter_001_paragraph_002",
                            "paragraph_no": 2,
                            "text": "宝玉道：“我来了。”贾母命他坐下。",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "passage_id": "passage_000003",
                            "chapter_id": "chapter_001",
                            "paragraph_id": "chapter_001_paragraph_003",
                            "paragraph_no": 3,
                            "text": "甄宝玉与贾宝玉同名不同人。",
                        },
                        ensure_ascii=False,
                    ),
                    json.dumps(
                        {
                            "passage_id": "passage_000004",
                            "chapter_id": "chapter_001",
                            "paragraph_id": "chapter_001_paragraph_004",
                            "paragraph_no": 4,
                            "text": "众人说道：“宝玉这会子倒安静了。”",
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

    def test_build_all_generates_relations_and_evidence(self) -> None:
        """
        验证生成器会写出关系文件、证据文件、风格候选文件和来源报告。

        @params:
            无。

        @return:
            None。
        """
        builder = CharacterSkillBuilder()
        results = builder.build_all(self.skill_root, self.triples_file, self.passages_file)

        self.assertEqual(1, len(results))
        result = results[0]
        self.assertEqual("jia-baoyu", result.character_id)
        self.assertEqual(2, result.relation_count)
        self.assertEqual(3, result.evidence_count)
        self.assertEqual(3, result.ranked_evidence_count)
        self.assertEqual(1, result.style_evidence_count)
        self.assertEqual(2, result.style_summary_count)
        self.assertTrue((self.skill_dir / "relations.md").exists())
        self.assertTrue((self.skill_dir / "evidence_passages.jsonl").exists())
        self.assertTrue((self.skill_dir / "evidence_ranked.jsonl").exists())
        self.assertTrue((self.skill_dir / "style_evidence.jsonl").exists())
        self.assertTrue((self.skill_dir / "style_summary_candidates.json").exists())
        self.assertTrue((self.skill_dir / "source_report.json").exists())

    def test_exclude_terms_only_remove_false_positive_occurrences(self) -> None:
        """
        验证排除词会过滤误命中，但不会误删同段中的有效人物提及。

        @params:
            无。

        @return:
            None。
        """
        builder = CharacterSkillBuilder()
        builder.build_all(self.skill_root, self.triples_file, self.passages_file)

        evidence_lines = (self.skill_dir / "evidence_passages.jsonl").read_text(encoding="utf-8").splitlines()
        evidence = [json.loads(line) for line in evidence_lines if line.strip()]

        self.assertEqual(["passage_000002", "passage_000003", "passage_000004"], [item["passage_id"] for item in evidence])
        self.assertEqual(["宝玉"], evidence[0]["matched_terms"])
        self.assertIn("贾宝玉", evidence[1]["matched_terms"])

    def test_generated_markdown_is_evidence_first(self) -> None:
        """
        验证生成后的 Markdown 文件改为输出带证据支撑的风格结论。

        @params:
            无。

        @return:
            None。
        """
        builder = CharacterSkillBuilder()
        builder.build_all(self.skill_root, self.triples_file, self.passages_file)

        persona = (self.skill_dir / "persona.md").read_text(encoding="utf-8")
        style = (self.skill_dir / "style.md").read_text(encoding="utf-8")
        examples = (self.skill_dir / "examples.md").read_text(encoding="utf-8")

        self.assertIn("不写无证据的人物判断", persona)
        self.assertIn("## 当前风格结论", style)
        self.assertIn("## 证据基础", style)
        self.assertIn("直接发话证据稳定", style)
        self.assertIn("`chapter_001` / `passage_000002`", style)
        self.assertIn("不自动生成角色回答示例", examples)

    def test_style_summary_candidates_are_evidence_backed(self) -> None:
        """
        验证风格候选结论会绑定明确的段落和章节证据。

        @params:
            无。

        @return:
            None。
        """
        builder = CharacterSkillBuilder()
        builder.build_all(self.skill_root, self.triples_file, self.passages_file)

        candidates = json.loads((self.skill_dir / "style_summary_candidates.json").read_text(encoding="utf-8"))

        self.assertEqual(2, len(candidates))
        self.assertEqual("direct_speech_presence", candidates[0]["trait"])
        self.assertEqual(["passage_000002"], candidates[0]["evidence_passage_ids"])
        self.assertEqual(["chapter_001"], candidates[0]["evidence_chapter_ids"])
        self.assertEqual(1, candidates[0]["signal_count"])

    def test_ranked_and_style_evidence_capture_noise_reduction(self) -> None:
        """
        验证去噪结果包含分数与噪声标记，风格证据只保留更强信号段落。

        @params:
            无。

        @return:
            None。
        """
        builder = CharacterSkillBuilder()
        builder.build_all(self.skill_root, self.triples_file, self.passages_file)

        ranked_lines = (self.skill_dir / "evidence_ranked.jsonl").read_text(encoding="utf-8").splitlines()
        ranked = [json.loads(line) for line in ranked_lines if line.strip()]
        style_lines = (self.skill_dir / "style_evidence.jsonl").read_text(encoding="utf-8").splitlines()
        style = [json.loads(line) for line in style_lines if line.strip()]

        self.assertEqual(3, len(ranked))
        self.assertEqual(1, len(style))
        self.assertIn("contains_target_speech_marker", ranked[0]["signals"])
        self.assertEqual("passage_000002", style[0]["passage_id"])
        self.assertEqual("speech_marker", style[0]["signal_type"])

        other_speaker_item = next(item for item in ranked if item["passage_id"] == "passage_000004")
        self.assertIn("target_not_confirmed_as_speaker", other_speaker_item["noise_flags"])
        self.assertIn("generic_speaker_context", other_speaker_item["noise_flags"])


if __name__ == "__main__":
    unittest.main()
