"""
人物对话检索器

支持格式：
1. 人物 skill 目录中的 manifest.json、persona.md、style.md、boundaries.md、relations.md
2. evidence_ranked.jsonl
3. style_evidence.jsonl

输出：
1. 人物对话检索结果
2. 角色基础资产摘要

用法：
    from pathlib import Path
    from tools.characterchat.retriever import CharacterChatRetriever

    retriever = CharacterChatRetriever()
    result = retriever.retrieve(
        skill_root=Path("skill/characters"),
        character_id="jia-baoyu",
        user_query="你怎么看黛玉？",
    )
"""

from __future__ import annotations

import json
import re
from pathlib import Path


class CharacterChatRetriever:
    """读取人物 skill 资产并执行第一版证据检索。"""

    # 单个角色返回的默认风格证据条数。
    DEFAULT_STYLE_TOP_K = 3
    # 单个角色返回的默认事实证据条数。
    DEFAULT_FACT_TOP_K = 5
    # 单个角色返回的默认关系条数。
    DEFAULT_RELATION_TOP_K = 8

    def retrieve(
        self,
        skill_root: Path,
        character_id: str,
        user_query: str,
        style_top_k: int = DEFAULT_STYLE_TOP_K,
        fact_top_k: int = DEFAULT_FACT_TOP_K,
        relation_top_k: int = DEFAULT_RELATION_TOP_K,
    ) -> dict[str, object]:
        """
        按角色和用户问题加载 skill 资产，并返回 prompt 组装所需上下文。

        @params:
            skill_root: 人物 skill 根目录。
            character_id: 人物唯一 ID。
            user_query: 用户问题。
            style_top_k: 返回的风格证据条数。
            fact_top_k: 返回的事实证据条数。
            relation_top_k: 返回的关系条数。

        @return:
            检索结果字典，包含角色资产、关系、证据和查询项。
        """
        skill_dir = self.resolve_skill_dir(skill_root, character_id)
        manifest = self.load_json(skill_dir / "manifest.json")
        source_report = self.load_json(skill_dir / "source_report.json")
        persona_markdown = (skill_dir / "persona.md").read_text(encoding="utf-8")
        style_markdown = (skill_dir / "style.md").read_text(encoding="utf-8")
        boundaries_markdown = (skill_dir / "boundaries.md").read_text(encoding="utf-8")
        relations = self.load_relations(skill_dir / "relations.md")
        style_evidence = self.load_jsonl(skill_dir / "style_evidence.jsonl")
        ranked_evidence = self.load_jsonl(skill_dir / "evidence_ranked.jsonl")

        query_terms = self.extract_query_terms(user_query, manifest, relations)
        selected_relations = self.select_relations(relations, query_terms, relation_top_k)
        selected_style_evidence = self.select_style_evidence(style_evidence, user_query, query_terms, style_top_k)
        selected_fact_evidence = self.select_fact_evidence(
            ranked_evidence,
            selected_style_evidence,
            user_query,
            query_terms,
            fact_top_k,
        )

        return {
            "character": {
                "id": manifest["id"],
                "name": manifest["name"],
                "aliases": list(manifest.get("aliases", [])),
                "skill_dir": str(skill_dir),
            },
            "user_query": user_query,
            "query_terms": query_terms,
            "constraints": {
                "persona_markdown": persona_markdown,
                "style_markdown": style_markdown,
                "boundaries_markdown": boundaries_markdown,
            },
            "retrieval": {
                "relations": selected_relations,
                "style_evidence": selected_style_evidence,
                "fact_evidence": selected_fact_evidence,
            },
            "source_report": source_report,
        }

    def resolve_skill_dir(self, skill_root: Path, character_id: str) -> Path:
        """
        根据 character_id 定位对应的人物 skill 目录。

        @params:
            skill_root: 人物 skill 根目录。
            character_id: 人物唯一 ID。

        @return:
            命中的人物 skill 目录路径。
        """
        for skill_dir in sorted(path for path in skill_root.iterdir() if path.is_dir() and path.name.endswith(".skill")):
            manifest_file = skill_dir / "manifest.json"
            if not manifest_file.exists():
                continue
            manifest = self.load_json(manifest_file)
            if manifest.get("id") == character_id:
                return skill_dir
        raise FileNotFoundError(f"Character skill not found for character_id={character_id}")

    def load_json(self, file_path: Path) -> dict[str, object]:
        """
        读取一份 JSON 文件。

        @params:
            file_path: JSON 文件路径。

        @return:
            解析后的 JSON 字典。
        """
        return json.loads(file_path.read_text(encoding="utf-8"))

    def load_jsonl(self, file_path: Path) -> list[dict[str, object]]:
        """
        读取一份 JSONL 文件。

        @params:
            file_path: JSONL 文件路径。

        @return:
            解析后的字典列表。
        """
        return [json.loads(line) for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def load_relations(self, file_path: Path) -> list[dict[str, str]]:
        """
        从 relations.md 中提取结构化关系列表。

        @params:
            file_path: relations.md 文件路径。

        @return:
            结构化关系字典列表。
        """
        relations: list[dict[str, str]] = []
        pattern = re.compile(r"^- `(.+)` -- `(.+)`（(.+)）--> `(.+)`$")

        for line in file_path.read_text(encoding="utf-8").splitlines():
            matcher = pattern.match(line.strip())
            if matcher:
                relations.append(
                    {
                        "head": matcher.group(1),
                        "relation": matcher.group(2),
                        "label": matcher.group(3),
                        "tail": matcher.group(4),
                    }
                )

        return relations

    def extract_query_terms(
        self,
        user_query: str,
        manifest: dict[str, object],
        relations: list[dict[str, str]],
    ) -> list[str]:
        """
        从用户问题中抽取当前检索阶段使用的关键词。

        @params:
            user_query: 用户问题。
            manifest: 人物 manifest 内容。
            relations: 结构化关系列表。

        @return:
            关键词列表，按长度从长到短排序。
        """
        query_terms: set[str] = set()
        retrieval_hint = manifest.get("retrieval_hint", {})
        keywords = list(retrieval_hint.get("character_keywords", []))
        aliases = list(manifest.get("aliases", []))
        names = [manifest.get("name", ""), *aliases, *keywords]

        for item in names:
            if isinstance(item, str) and item and item in user_query:
                query_terms.add(item)

        for relation in relations:
            for candidate in (relation["head"], relation["tail"], relation["label"]):
                if candidate and candidate in user_query:
                    query_terms.add(candidate)

        return sorted(query_terms, key=lambda item: (-len(item), item))

    def select_relations(
        self,
        relations: list[dict[str, str]],
        query_terms: list[str],
        top_k: int,
    ) -> list[dict[str, object]]:
        """
        根据用户问题对关系条目做简单排序，并返回前若干条。

        @params:
            relations: 结构化关系列表。
            query_terms: 检索关键词列表。
            top_k: 返回的关系条数。

        @return:
            排序后的关系字典列表。
        """
        scored_relations: list[tuple[int, dict[str, str]]] = []

        for relation in relations:
            score = 0
            if any(term in relation["head"] or term in relation["tail"] or term in relation["label"] for term in query_terms):
                score += 5
            scored_relations.append((score, relation))

        scored_relations.sort(key=lambda item: (-item[0], item[1]["head"], item[1]["tail"], item[1]["relation"]))
        if query_terms and any(score > 0 for score, _ in scored_relations):
            scored_relations = [(score, relation) for score, relation in scored_relations if score > 0]

        selected = [relation | {"score": score} for score, relation in scored_relations[:top_k]]
        return selected

    def select_style_evidence(
        self,
        style_evidence: list[dict[str, object]],
        user_query: str,
        query_terms: list[str],
        top_k: int,
    ) -> list[dict[str, object]]:
        """
        对风格证据做简单重排，优先返回更贴近用户问题的段落。

        @params:
            style_evidence: 风格证据列表。
            user_query: 用户问题。
            query_terms: 检索关键词列表。
            top_k: 返回的风格证据条数。

        @return:
            排序后的风格证据字典列表。
        """
        return self.rank_evidence_items(style_evidence, user_query, query_terms, top_k, prefer_style=True)

    def select_fact_evidence(
        self,
        ranked_evidence: list[dict[str, object]],
        selected_style_evidence: list[dict[str, object]],
        user_query: str,
        query_terms: list[str],
        top_k: int,
    ) -> list[dict[str, object]]:
        """
        对去噪证据做重排，并排除已选入风格证据的段落。

        @params:
            ranked_evidence: 去噪证据列表。
            selected_style_evidence: 已选中的风格证据列表。
            user_query: 用户问题。
            query_terms: 检索关键词列表。
            top_k: 返回的事实证据条数。

        @return:
            排序后的事实证据字典列表。
        """
        excluded_ids = {item["passage_id"] for item in selected_style_evidence}
        filtered = [item for item in ranked_evidence if item["passage_id"] not in excluded_ids]
        return self.rank_evidence_items(filtered, user_query, query_terms, top_k, prefer_style=False)

    def rank_evidence_items(
        self,
        items: list[dict[str, object]],
        user_query: str,
        query_terms: list[str],
        top_k: int,
        prefer_style: bool,
    ) -> list[dict[str, object]]:
        """
        对证据项执行第一版启发式重排。

        @params:
            items: 待排序证据列表。
            user_query: 用户问题。
            query_terms: 检索关键词列表。
            top_k: 返回条数。
            prefer_style: 是否偏向风格证据。

        @return:
            排序后的证据字典列表。
        """
        scored_items: list[tuple[int, dict[str, object]]] = []

        for item in items:
            score = int(item.get("score", 0))
            text = str(item.get("text", ""))

            if user_query and len(user_query) >= 2 and user_query in text:
                score += 6

            matched_terms = [term for term in query_terms if term and term in text]
            score += len(matched_terms) * 2

            if prefer_style and item.get("signal_type") == "speech_marker":
                score += 3

            if prefer_style and "contains_speech_marker" in item.get("signals", []):
                score += 2

            scored_items.append((score, item | {"retrieval_score": score, "matched_query_terms": matched_terms}))

        scored_items.sort(
            key=lambda pair: (
                -pair[0],
                str(pair[1].get("chapter_id", "")),
                int(pair[1].get("paragraph_no", 0)),
                str(pair[1].get("passage_id", "")),
            )
        )
        return [item for _, item in scored_items[:top_k]]
