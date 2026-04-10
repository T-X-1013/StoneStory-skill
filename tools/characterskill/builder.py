"""
人物 skill 第一版生成器

支持格式：
1. manifest.json（人物基础配置）
2. triples.csv（人际关系三元组）
3. passages.jsonl（原文段落证据）

输出：
1. relations.md
2. evidence_passages.jsonl
3. evidence_ranked.jsonl
4. style_evidence.jsonl
5. source_report.json
6. persona.md
7. style.md
8. examples.md

用法：
    from pathlib import Path
    from tools.characterskill.builder import CharacterSkillBuilder

    builder = CharacterSkillBuilder()
    results = builder.build_all(
        skill_root=Path("skill/characters"),
        triples_file=Path("data/input/triples.csv"),
        passages_file=Path("data/output/passages.jsonl"),
    )
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import (
    CharacterEvidence,
    CharacterManifest,
    CharacterRelation,
    CharacterSkillResult,
    RankedCharacterEvidence,
    StyleCharacterEvidence,
)


class CharacterSkillBuilder:
    """基于关系数据和原文段落，为人物 skill 生成第一版证据资产。"""

    # 常见人物发话标记，用于提炼风格证据。
    SPEECH_MARKERS = ("道", "说道", "笑道", "问道", "答道", "叹道", "骂道", "忙道")

    def build_all(self, skill_root: Path, triples_file: Path, passages_file: Path) -> list[CharacterSkillResult]:
        """
        读取全部人物 manifest，并批量生成人物 skill 资产。

        @params:
            skill_root: 人物 skill 根目录。
            triples_file: 关系三元组 CSV 文件路径。
            passages_file: 原文段落 JSONL 文件路径。

        @return:
            构建结果列表，每个元素对应一个人物 skill。
        """
        manifests = self.load_manifests(skill_root)
        relation_rows = self.load_relation_rows(triples_file)
        passages = self.load_passages(passages_file)
        results: list[CharacterSkillResult] = []

        for manifest in manifests:
            results.append(self.build_character_skill(manifest, relation_rows, passages, triples_file, passages_file))

        return results

    def load_manifests(self, skill_root: Path) -> list[CharacterManifest]:
        """
        扫描人物 skill 目录并加载所有 manifest.json。

        @params:
            skill_root: 人物 skill 根目录。

        @return:
            人物 manifest 列表。
        """
        manifests: list[CharacterManifest] = []

        for skill_dir in sorted(path for path in skill_root.iterdir() if path.is_dir() and path.name.endswith(".skill")):
            manifest_file = skill_dir / "manifest.json"
            manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
            retrieval_hint = manifest_data.get("retrieval_hint", {})

            manifests.append(
                CharacterManifest(
                    skill_dir=skill_dir,
                    character_id=manifest_data["id"],
                    name=manifest_data["name"],
                    aliases=list(manifest_data.get("aliases", [])),
                    retrieval_keywords=list(retrieval_hint.get("character_keywords", [])),
                    evidence_terms=list(manifest_data.get("evidence_terms", [])),
                    exclude_terms=list(manifest_data.get("exclude_terms", [])),
                )
            )

        return manifests

    def load_relation_rows(self, triples_file: Path) -> list[dict[str, str]]:
        """
        读取关系 CSV，并保留 head、tail、relation、label 四列。

        @params:
            triples_file: 关系三元组 CSV 文件路径。

        @return:
            关系字典列表。
        """
        with triples_file.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            return [
                {
                    "head": row["head"].strip(),
                    "tail": row["tail"].strip(),
                    "relation": row["relation"].strip(),
                    "label": row["label"].strip(),
                }
                for row in reader
            ]

    def load_passages(self, passages_file: Path) -> list[dict[str, object]]:
        """
        读取 passages.jsonl 中的全部段落对象。

        @params:
            passages_file: 段落 JSONL 文件路径。

        @return:
            段落字典列表。
        """
        return [
            json.loads(line)
            for line in passages_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def build_character_skill(
        self,
        manifest: CharacterManifest,
        relation_rows: list[dict[str, str]],
        passages: list[dict[str, object]],
        triples_file: Path,
        passages_file: Path,
    ) -> CharacterSkillResult:
        """
        为单个人物 skill 生成关系、证据和说明文件。

        @params:
            manifest: 人物 manifest 配置。
            relation_rows: 关系三元组列表。
            passages: 原文段落列表。
            triples_file: 关系三元组 CSV 文件路径。
            passages_file: 段落 JSONL 文件路径。

        @return:
            单个人物 skill 的构建结果对象。
        """
        relations = self.collect_relations(manifest, relation_rows)
        evidence = self.collect_evidence(manifest, passages)
        ranked_evidence = self.rank_evidence(manifest, evidence)
        style_evidence = self.extract_style_evidence(manifest, ranked_evidence)

        relations_output = manifest.skill_dir / "relations.md"
        evidence_output = manifest.skill_dir / "evidence_passages.jsonl"
        ranked_evidence_output = manifest.skill_dir / "evidence_ranked.jsonl"
        style_evidence_output = manifest.skill_dir / "style_evidence.jsonl"
        report_output = manifest.skill_dir / "source_report.json"

        self.write_relations_markdown(manifest, relations, relations_output)
        self.write_evidence_jsonl(evidence, evidence_output)
        self.write_ranked_evidence_jsonl(ranked_evidence, ranked_evidence_output)
        self.write_style_evidence_jsonl(style_evidence, style_evidence_output)
        self.write_source_report(
            manifest,
            relations,
            evidence,
            ranked_evidence,
            style_evidence,
            triples_file,
            passages_file,
            report_output,
        )
        self.write_persona_markdown(manifest, relations, evidence, manifest.skill_dir / "persona.md")
        self.write_style_markdown(manifest, ranked_evidence, style_evidence, manifest.skill_dir / "style.md")
        self.write_examples_markdown(manifest, manifest.skill_dir / "examples.md")
        self.write_skill_readme(manifest, manifest.skill_dir / "README.md")

        return CharacterSkillResult(
            character_id=manifest.character_id,
            character_name=manifest.name,
            skill_dir=manifest.skill_dir,
            relation_count=len(relations),
            evidence_count=len(evidence),
            ranked_evidence_count=len(ranked_evidence),
            style_evidence_count=len(style_evidence),
            relations_output=relations_output,
            evidence_output=evidence_output,
            ranked_evidence_output=ranked_evidence_output,
            style_evidence_output=style_evidence_output,
            report_output=report_output,
        )

    def collect_relations(
        self,
        manifest: CharacterManifest,
        relation_rows: list[dict[str, str]],
    ) -> list[CharacterRelation]:
        """
        从关系三元组中筛出与人物直接相关的记录。

        @params:
            manifest: 人物 manifest 配置。
            relation_rows: 关系三元组列表。

        @return:
            与人物直接相关的关系对象列表。
        """
        identity_terms = set(manifest.identity_terms)
        relations = [
            CharacterRelation(
                head=row["head"],
                tail=row["tail"],
                relation=row["relation"],
                label=row["label"],
            )
            for row in relation_rows
            if row["head"] in identity_terms or row["tail"] in identity_terms
        ]

        return sorted(relations, key=lambda item: (item.head != manifest.name, item.head, item.tail, item.relation))

    def collect_evidence(
        self,
        manifest: CharacterManifest,
        passages: list[dict[str, object]],
    ) -> list[CharacterEvidence]:
        """
        从 passages.jsonl 中提取命中人物识别词的原文证据段落。

        @params:
            manifest: 人物 manifest 配置。
            passages: 原文段落列表。

        @return:
            人物证据段落列表。
        """
        evidence: list[CharacterEvidence] = []
        evidence_terms = self.resolve_evidence_terms(manifest)

        for passage in passages:
            text = str(passage["text"])
            matched_terms = self.match_evidence_terms(text, evidence_terms, manifest.exclude_terms)
            if not matched_terms:
                continue

            evidence.append(
                CharacterEvidence(
                    character_id=manifest.character_id,
                    character_name=manifest.name,
                    chapter_id=str(passage["chapter_id"]),
                    passage_id=str(passage["passage_id"]),
                    paragraph_id=str(passage["paragraph_id"]),
                    paragraph_no=int(passage["paragraph_no"]),
                    matched_terms=matched_terms,
                    text=text,
                )
            )

        return evidence

    def rank_evidence(
        self,
        manifest: CharacterManifest,
        evidence: list[CharacterEvidence],
    ) -> list[RankedCharacterEvidence]:
        """
        为人物证据段落打相关性分数，并添加噪声标记。

        @params:
            manifest: 人物 manifest 配置。
            evidence: 原始人物证据段落列表。

        @return:
            按分数和位置排序后的去噪证据段落列表。
        """
        ranked_items: list[RankedCharacterEvidence] = []

        for item in evidence:
            score = 0
            signals: list[str] = []
            noise_flags: list[str] = []
            text = item.text

            if manifest.name in text:
                score += 5
                signals.append("contains_full_name")

            if any(alias in text for alias in manifest.aliases):
                score += 2
                signals.append("contains_alias")

            if len(item.matched_terms) >= 2:
                score += 2
                signals.append("matched_multiple_terms")

            if "“" in text and "”" in text:
                score += 2
                signals.append("contains_dialogue_quotes")

            if self.contains_speech_signal(text, manifest):
                score += 3
                signals.append("contains_speech_marker")

            if self.contains_arrival_or_presence_signal(text, item.matched_terms):
                score += 1
                signals.append("contains_presence_signal")

            if manifest.name not in text and all(len(term) <= 2 for term in item.matched_terms):
                score -= 2
                noise_flags.append("short_alias_only")

            if "通灵宝玉" in text:
                score -= 3
                noise_flags.append("contains_object_name")

            if "甄宝玉" in text:
                score -= 3
                noise_flags.append("contains_other_character_name")

            if "“" not in text and "”" not in text and not self.contains_speech_signal(text, manifest):
                score -= 1
                noise_flags.append("no_dialogue_signal")

            ranked_items.append(
                RankedCharacterEvidence(
                    character_id=item.character_id,
                    character_name=item.character_name,
                    chapter_id=item.chapter_id,
                    passage_id=item.passage_id,
                    paragraph_id=item.paragraph_id,
                    paragraph_no=item.paragraph_no,
                    matched_terms=item.matched_terms,
                    score=score,
                    signals=signals,
                    noise_flags=noise_flags,
                    text=item.text,
                )
            )

        return sorted(
            ranked_items,
            key=lambda item: (-item.score, item.chapter_id, item.paragraph_no, item.passage_id),
        )

    def extract_style_evidence(
        self,
        manifest: CharacterManifest,
        ranked_evidence: list[RankedCharacterEvidence],
    ) -> list[StyleCharacterEvidence]:
        """
        从去噪证据中筛出更适合做说话风格分析的段落。

        @params:
            manifest: 人物 manifest 配置。
            ranked_evidence: 去噪后的证据段落列表。

        @return:
            风格证据段落列表。
        """
        style_items: list[StyleCharacterEvidence] = []

        for item in ranked_evidence:
            signal_type = self.detect_style_signal_type(item.text, manifest)
            if signal_type is None:
                continue
            if item.score < 2:
                continue

            style_items.append(
                StyleCharacterEvidence(
                    character_id=item.character_id,
                    character_name=item.character_name,
                    chapter_id=item.chapter_id,
                    passage_id=item.passage_id,
                    paragraph_id=item.paragraph_id,
                    paragraph_no=item.paragraph_no,
                    matched_terms=item.matched_terms,
                    score=item.score,
                    signal_type=signal_type,
                    signals=item.signals,
                    text=item.text,
                )
            )

        return style_items

    def resolve_evidence_terms(self, manifest: CharacterManifest) -> list[str]:
        """
        返回人物证据提取时使用的包含词列表。

        @params:
            manifest: 人物 manifest 配置。

        @return:
            去重并按长度排序后的证据包含词列表。
        """
        source_terms = manifest.evidence_terms or manifest.identity_terms
        return sorted((term for term in source_terms if term), key=lambda item: (-len(item), item))

    def match_evidence_terms(self, text: str, evidence_terms: list[str], exclude_terms: list[str]) -> list[str]:
        """
        在一段文本中匹配人物证据词，并排除仅出现在排除短语中的命中。

        @params:
            text: 待匹配的原文段落。
            evidence_terms: 人物证据包含词列表。
            exclude_terms: 人物证据排除词列表。

        @return:
            本段文本中有效命中的证据词列表。
        """
        exclude_spans = self.find_text_spans(text, exclude_terms)
        matched_terms: list[str] = []

        for term in evidence_terms:
            if self.has_valid_occurrence(text, term, exclude_spans):
                matched_terms.append(term)

        return matched_terms

    def find_text_spans(self, text: str, terms: list[str]) -> list[tuple[int, int]]:
        """
        返回若干词在文本中的全部命中区间。

        @params:
            text: 待搜索文本。
            terms: 待匹配词列表。

        @return:
            区间列表，每项为 (起始下标, 结束下标)。
        """
        spans: list[tuple[int, int]] = []

        for term in terms:
            start = text.find(term)
            while start != -1:
                spans.append((start, start + len(term)))
                start = text.find(term, start + 1)

        return spans

    def has_valid_occurrence(self, text: str, term: str, exclude_spans: list[tuple[int, int]]) -> bool:
        """
        判断一个证据词在文本中的命中，是否存在不被排除短语覆盖的有效位置。

        @params:
            text: 待搜索文本。
            term: 当前证据词。
            exclude_spans: 排除短语命中区间列表。

        @return:
            若存在有效命中则返回 True，否则返回 False。
        """
        start = text.find(term)
        while start != -1:
            end = start + len(term)
            if not any(span_start <= start and end <= span_end for span_start, span_end in exclude_spans):
                return True
            start = text.find(term, start + 1)
        return False

    def contains_speech_signal(self, text: str, manifest: CharacterManifest) -> bool:
        """
        判断一段文本中是否存在人物相关的发话信号。

        @params:
            text: 待检查文本。
            manifest: 人物 manifest 配置。

        @return:
            若存在人物名与发话标记组合则返回 True，否则返回 False。
        """
        for term in manifest.identity_terms:
            for marker in self.SPEECH_MARKERS:
                if f"{term}{marker}" in text:
                    return True
        return False

    def contains_arrival_or_presence_signal(self, text: str, matched_terms: list[str]) -> bool:
        """
        判断文本中是否出现“来了、见了、看见了”等人物在场信号。

        @params:
            text: 待检查文本。
            matched_terms: 当前段落命中的人物识别词。

        @return:
            若存在人物在场信号则返回 True，否则返回 False。
        """
        presence_suffixes = ("来了", "来了！", "来了。", "来至", "见了", "看见", "忙来", "归坐")
        return any(any(f"{term}{suffix}" in text for suffix in presence_suffixes) for term in matched_terms)

    def detect_style_signal_type(self, text: str, manifest: CharacterManifest) -> str | None:
        """
        识别一条段落是否适合作为说话风格证据，并返回信号类型。

        @params:
            text: 待识别文本。
            manifest: 人物 manifest 配置。

        @return:
            风格证据类型；若不适合作为风格证据则返回 None。
        """
        if self.contains_speech_signal(text, manifest):
            return "speech_marker"
        if "“" in text and "”" in text and manifest.name in text:
            return "named_dialogue_context"
        return None

    def write_relations_markdown(
        self,
        manifest: CharacterManifest,
        relations: list[CharacterRelation],
        output_file: Path,
    ) -> None:
        """
        将人物关系写成 Markdown 文件，便于人工阅读和后续维护。

        @params:
            manifest: 人物 manifest 配置。
            relations: 与人物直接相关的关系对象列表。
            output_file: relations.md 输出路径。

        @return:
            None。
        """
        lines = [
            f"# {manifest.name} Relations",
            "",
            "## 生成说明",
            "",
            "- 本文件由 `tools/characterskill` 基于 `data/input/triples.csv` 自动生成。",
            "- 当前版本只整理与该人物直接相关的三元组，不做额外人物解读。",
            "",
            "## 关系列表",
            "",
        ]

        if not relations:
            lines.extend(["- 当前未在 `triples.csv` 中发现与该人物直接相关的三元组。", ""])
        else:
            for relation in relations:
                lines.append(f"- `{relation.head}` -- `{relation.relation}`（{relation.label}）--> `{relation.tail}`")
            lines.append("")

        output_file.write_text("\n".join(lines), encoding="utf-8")

    def write_evidence_jsonl(self, evidence: list[CharacterEvidence], output_file: Path) -> None:
        """
        将命中人物识别词的原文段落写成 JSONL 文件。

        @params:
            evidence: 人物证据段落列表。
            output_file: evidence_passages.jsonl 输出路径。

        @return:
            None。
        """
        content = "\n".join(json.dumps(item.to_dict(), ensure_ascii=False) for item in evidence)
        output_file.write_text((content + "\n") if content else "", encoding="utf-8")

    def write_ranked_evidence_jsonl(
        self,
        ranked_evidence: list[RankedCharacterEvidence],
        output_file: Path,
    ) -> None:
        """
        将去噪打分后的证据段落写成 JSONL 文件。

        @params:
            ranked_evidence: 去噪后的证据段落列表。
            output_file: evidence_ranked.jsonl 输出路径。

        @return:
            None。
        """
        content = "\n".join(json.dumps(item.to_dict(), ensure_ascii=False) for item in ranked_evidence)
        output_file.write_text((content + "\n") if content else "", encoding="utf-8")

    def write_style_evidence_jsonl(
        self,
        style_evidence: list[StyleCharacterEvidence],
        output_file: Path,
    ) -> None:
        """
        将适合做说话风格分析的证据段落写成 JSONL 文件。

        @params:
            style_evidence: 风格证据段落列表。
            output_file: style_evidence.jsonl 输出路径。

        @return:
            None。
        """
        content = "\n".join(json.dumps(item.to_dict(), ensure_ascii=False) for item in style_evidence)
        output_file.write_text((content + "\n") if content else "", encoding="utf-8")

    def write_source_report(
        self,
        manifest: CharacterManifest,
        relations: list[CharacterRelation],
        evidence: list[CharacterEvidence],
        ranked_evidence: list[RankedCharacterEvidence],
        style_evidence: list[StyleCharacterEvidence],
        triples_file: Path,
        passages_file: Path,
        output_file: Path,
    ) -> None:
        """
        写出当前人物 skill 的数据来源和计数摘要。

        @params:
            manifest: 人物 manifest 配置。
            relations: 与人物直接相关的关系对象列表。
            evidence: 人物证据段落列表。
            ranked_evidence: 去噪后的证据段落列表。
            style_evidence: 风格证据段落列表。
            triples_file: 关系三元组 CSV 文件路径。
            passages_file: 段落 JSONL 文件路径。
            output_file: source_report.json 输出路径。

        @return:
            None。
        """
        relation_labels: dict[str, int] = {}
        for relation in relations:
            relation_labels[relation.label] = relation_labels.get(relation.label, 0) + 1

        evidence_terms = self.resolve_evidence_terms(manifest)
        report = {
            "character_id": manifest.character_id,
            "character_name": manifest.name,
            "aliases": manifest.aliases,
            "identity_terms": manifest.identity_terms,
            "evidence_terms": evidence_terms,
            "exclude_terms": manifest.exclude_terms,
            "relation_count": len(relations),
            "evidence_count": len(evidence),
            "ranked_evidence_count": len(ranked_evidence),
            "style_evidence_count": len(style_evidence),
            "relation_label_counts": relation_labels,
            "source_files": {
                "triples_csv": str(triples_file),
                "passages_jsonl": str(passages_file),
                "manifest_json": str(manifest.skill_dir / "manifest.json"),
            },
        }
        output_file.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def write_persona_markdown(
        self,
        manifest: CharacterManifest,
        relations: list[CharacterRelation],
        evidence: list[CharacterEvidence],
        output_file: Path,
    ) -> None:
        """
        写出人物 persona 文件的第一版数据摘要。

        @params:
            manifest: 人物 manifest 配置。
            relations: 与人物直接相关的关系对象列表。
            evidence: 人物证据段落列表。
            output_file: persona.md 输出路径。

        @return:
            None。
        """
        aliases_text = "、".join(manifest.aliases) if manifest.aliases else "无"
        lines = [
            f"# {manifest.name} Persona",
            "",
            "## 生成说明",
            "",
            "- 本文件由 `tools/characterskill` 自动生成。",
            "- 当前版本只保留可直接从输入数据确认的信息，不写无证据的人物判断。",
            "",
            "## 基础信息",
            "",
            f"- `character_id`：`{manifest.character_id}`",
            f"- `name`：{manifest.name}",
            f"- `aliases`：{aliases_text}",
            "",
            "## 数据概览",
            "",
            f"- 直接关系条数：{len(relations)}",
            f"- 原文证据段落条数：{len(evidence)}",
            "- 直接关系明细：见 `relations.md`",
            "- 原文证据明细：见 `evidence_passages.jsonl`",
            "",
            "## 当前约束",
            "",
            "- 不根据常识或印象补写人物性格结论。",
            "- 后续若要补充人物画像，应为每条结论绑定章节或段落证据。",
            "",
        ]
        output_file.write_text("\n".join(lines), encoding="utf-8")

    def write_style_markdown(
        self,
        manifest: CharacterManifest,
        ranked_evidence: list[RankedCharacterEvidence],
        style_evidence: list[StyleCharacterEvidence],
        output_file: Path,
    ) -> None:
        """
        写出人物 style 文件的第一版说明。

        @params:
            manifest: 人物 manifest 配置。
            ranked_evidence: 去噪后的证据段落列表。
            style_evidence: 风格证据段落列表。
            output_file: style.md 输出路径。

        @return:
            None。
        """
        lines = [
            f"# {manifest.name} Style",
            "",
            "## 当前状态",
            "",
            "- 当前版本不自动写入说话风格结论。",
            "- 原因：现有输入文件可直接支持关系事实和原文证据抽取，但尚未建立可靠的风格提炼规则。",
            "",
            "## 已有证据基础",
            "",
            f"- 原始证据段落数：{len(ranked_evidence)}",
            f"- 风格证据段落数：{len(style_evidence)}",
            "- 证据文件：`evidence_passages.jsonl`",
            "- 去噪结果：`evidence_ranked.jsonl`",
            "- 风格证据：`style_evidence.jsonl`",
            "",
            "## 当前筛选规则",
            "",
            "- 去噪阶段会对命中主名、别名、引语、发话标记等信号打分。",
            "- 风格证据阶段优先保留带有人物发话标记或明确对话上下文的段落。",
            "",
            "## 后续约束",
            "",
            "- 风格结论必须可回溯到原文证据。",
            "- 不得根据主观印象直接写入角色语气、价值倾向或心理判断。",
            "",
        ]
        output_file.write_text("\n".join(lines), encoding="utf-8")

    def write_examples_markdown(self, manifest: CharacterManifest, output_file: Path) -> None:
        """
        写出人物 examples 文件的第一版占位说明。

        @params:
            manifest: 人物 manifest 配置。
            output_file: examples.md 输出路径。

        @return:
            None。
        """
        lines = [
            f"# {manifest.name} Examples",
            "",
            "## 当前状态",
            "",
            "- 当前版本不自动生成角色回答示例。",
            "- 原因：完整示例容易混入输入数据之外的主观补写。",
            "",
            "## 后续要求",
            "",
            "- 示例必须基于 `evidence_passages.jsonl` 中的原文证据生成或人工编写。",
            "- 若引用原文，应明确关联 `chapter_id` 与 `passage_id`。",
            "",
        ]
        output_file.write_text("\n".join(lines), encoding="utf-8")

    def write_skill_readme(self, manifest: CharacterManifest, output_file: Path) -> None:
        """
        更新人物 skill 目录的说明文件，明确哪些文件由工具生成。

        @params:
            manifest: 人物 manifest 配置。
            output_file: README.md 输出路径。

        @return:
            None。
        """
        lines = [
            f"# {manifest.name} Skill",
            "",
            f"该目录定义 `{manifest.name}` 的人物 skill 资产。",
            "",
            "当前文件分工：",
            "",
            "- `manifest.json`：给程序读取的人物标识、别名和检索提示",
            "- `relations.md`：基于 `data/input/triples.csv` 生成的人际关系清单",
            "- `evidence_passages.jsonl`：基于 `data/output/passages.jsonl` 提取的原文证据段落",
            "- `evidence_ranked.jsonl`：对角色相关段落做去噪和相关性打分后的结果",
            "- `style_evidence.jsonl`：更适合做人物说话风格分析的证据子集",
            "- `source_report.json`：当前人物 skill 的数据来源和计数摘要",
            "- `persona.md`：数据约束版人物说明，不写无证据结论",
            "- `style.md`：风格提炼约束说明",
            "- `boundaries.md`：运行时边界和禁止事项",
            "- `examples.md`：示例生成要求说明",
            "",
            "维护原则：",
            "",
            "- 事实知识优先来自输入数据和结构化输出，不凭印象补写人物设定。",
            "- 若后续补充人物画像或风格结论，必须给出可回溯证据。",
            "",
        ]
        output_file.write_text("\n".join(lines), encoding="utf-8")
