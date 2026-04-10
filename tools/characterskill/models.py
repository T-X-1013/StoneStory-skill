"""
人物 skill 数据模型

支持格式：
1. manifest.json
2. triples.csv
3. passages.jsonl

输出：
1. 人物 manifest 模型
2. 人物关系模型
3. 人物证据段落模型
4. 去噪后的证据模型
5. 风格证据模型
6. 人物 skill 构建结果模型

用法：
    from tools.characterskill.models import CharacterManifest, CharacterEvidence
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CharacterManifest:
    """表示一个人物 skill 的基础配置。"""

    skill_dir: Path               # 当前人物 skill 所在目录。
    character_id: str             # 人物唯一 ID，例如 jia-baoyu。
    name: str                     # 人物中文名，例如贾宝玉。
    aliases: list[str]            # 人物别名列表。
    retrieval_keywords: list[str] # manifest 中提供的检索提示关键词。
    evidence_terms: list[str]     # 原文证据检索时使用的包含词。
    exclude_terms: list[str]      # 原文证据检索时使用的排除词。

    @property
    def identity_terms(self) -> list[str]:
        """
        返回人物识别时使用的名称集合，按长度从长到短排序。

        @params:
            无。

        @return:
            去重后的身份识别词列表。
        """
        terms = {self.name, *self.aliases}
        return sorted((term for term in terms if term), key=lambda item: (-len(item), item))


@dataclass(frozen=True)
class CharacterRelation:
    """表示一条与人物直接相关的关系三元组。"""

    head: str      # 三元组头实体。
    tail: str      # 三元组尾实体。
    relation: str  # 关系英文编码。
    label: str     # 关系中文标签。


@dataclass(frozen=True)
class CharacterEvidence:
    """表示一条命中人物名称的原文证据段落。"""

    character_id: str        # 人物唯一 ID。
    character_name: str      # 人物中文名。
    chapter_id: str          # 所属章节 ID。
    passage_id: str          # 段落唯一 ID。
    paragraph_id: str        # 章内段落定位 ID。
    paragraph_no: int        # 章内段落序号。
    matched_terms: list[str] # 命中的人物识别词。
    text: str                # 原文段落正文。

    def to_dict(self) -> dict[str, object]:
        """
        将证据段落转换为可直接写入 JSONL 的字典结构。

        @params:
            无。

        @return:
            包含证据段落字段的字典对象。
        """
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "chapter_id": self.chapter_id,
            "passage_id": self.passage_id,
            "paragraph_id": self.paragraph_id,
            "paragraph_no": self.paragraph_no,
            "matched_terms": self.matched_terms,
            "text": self.text,
        }


@dataclass(frozen=True)
class RankedCharacterEvidence:
    """表示一条经过打分与去噪标记的角色相关证据段落。"""

    character_id: str        # 人物唯一 ID。
    character_name: str      # 人物中文名。
    chapter_id: str          # 所属章节 ID。
    passage_id: str          # 段落唯一 ID。
    paragraph_id: str        # 章内段落定位 ID。
    paragraph_no: int        # 章内段落序号。
    matched_terms: list[str] # 命中的人物识别词。
    score: int               # 当前段落的相关性得分。
    signals: list[str]       # 提升得分的信号列表。
    noise_flags: list[str]   # 降低可信度的噪声标记列表。
    text: str                # 原文段落正文。

    def to_dict(self) -> dict[str, object]:
        """
        将打分后的证据段落转换为可直接写入 JSONL 的字典结构。

        @params:
            无。

        @return:
            包含相关性得分、信号和正文的字典对象。
        """
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "chapter_id": self.chapter_id,
            "passage_id": self.passage_id,
            "paragraph_id": self.paragraph_id,
            "paragraph_no": self.paragraph_no,
            "matched_terms": self.matched_terms,
            "score": self.score,
            "signals": self.signals,
            "noise_flags": self.noise_flags,
            "text": self.text,
        }


@dataclass(frozen=True)
class StyleCharacterEvidence:
    """表示一条适合做人物说话风格分析的高质量证据段落。"""

    character_id: str        # 人物唯一 ID。
    character_name: str      # 人物中文名。
    chapter_id: str          # 所属章节 ID。
    passage_id: str          # 段落唯一 ID。
    paragraph_id: str        # 章内段落定位 ID。
    paragraph_no: int        # 章内段落序号。
    matched_terms: list[str] # 命中的人物识别词。
    score: int               # 当前段落的相关性得分。
    signal_type: str         # 风格证据类型，例如 direct_dialogue。
    signals: list[str]       # 命中的风格信号列表。
    text: str                # 原文段落正文。

    def to_dict(self) -> dict[str, object]:
        """
        将风格证据段落转换为可直接写入 JSONL 的字典结构。

        @params:
            无。

        @return:
            包含风格信号和正文的字典对象。
        """
        return {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "chapter_id": self.chapter_id,
            "passage_id": self.passage_id,
            "paragraph_id": self.paragraph_id,
            "paragraph_no": self.paragraph_no,
            "matched_terms": self.matched_terms,
            "score": self.score,
            "signal_type": self.signal_type,
            "signals": self.signals,
            "text": self.text,
        }


@dataclass(frozen=True)
class CharacterSkillResult:
    """表示单个人物 skill 的构建结果。"""

    character_id: str               # 人物唯一 ID。
    character_name: str             # 人物中文名。
    skill_dir: Path                 # 人物 skill 输出目录。
    relation_count: int             # 生成的关系条数。
    evidence_count: int             # 生成的原始证据段落条数。
    ranked_evidence_count: int      # 生成的去噪证据段落条数。
    style_evidence_count: int       # 生成的风格证据段落条数。
    relations_output: Path          # relations.md 输出路径。
    evidence_output: Path           # evidence_passages.jsonl 输出路径。
    ranked_evidence_output: Path    # evidence_ranked.jsonl 输出路径。
    style_evidence_output: Path     # style_evidence.jsonl 输出路径。
    report_output: Path             # source_report.json 输出路径。
