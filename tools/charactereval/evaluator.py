"""
人物对话评估器

支持格式：
1. prompt_payload.json
2. .txt 文件（纯文本角色回答）
3. .json 文件（结构化角色回答，支持 assistant_response/response/answer/content 和 cited_passage_ids）

输出：
1. 结构化 evaluation_report.json
2. 自动检查信号
3. 人工待填 rubric

用法：
    from pathlib import Path
    from tools.charactereval.evaluator import CharacterChatEvaluator

    evaluator = CharacterChatEvaluator()
    report = evaluator.evaluate_from_files(
        payload_file=Path("data/output/character_chat/jia-baoyu_prompt_payload.json"),
        response_text="妹妹自然是极好的人。",
        cited_passage_ids=["passage_001716"],
    )
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from .models import CharacterChatEvaluationReport, CharacterChatResponseInput


class CharacterChatEvaluator:
    """根据 prompt payload 和角色回答生成第一版评估报告。"""

    # 角色回答中常见的现代表达命中词，命中后仅作为风险提示，不直接判定失败。
    MODERN_EXPRESSION_TERMS = (
        "哈哈",
        "emo",
        "绝绝子",
        "打call",
        "粉丝",
        "AI",
        "OK",
        "YYDS",
        "666",
        "CPU",
    )
    # 角色回答中常见的不确定性提示词，命中时可视作“证据不足时有保守表达”的信号。
    UNCERTAINTY_TERMS = (
        "不能确定",
        "未敢定论",
        "不敢妄言",
        "难以断定",
        "未可知",
        "不好说",
    )
    # 评估报告中的人工评分项。
    MANUAL_RUBRIC_ITEMS = {
        "in_character": "回答是否像这个人物。",
        "answers_user_question": "回答是否正面回应了用户问题。",
        "grounded_in_evidence": "回答是否能回溯到检索证据。",
        "not_modernized": "回答是否避免了明显现代化表达。",
        "hallucination_risk": "回答是否存在较高胡编风险。",
    }

    def evaluate_from_files(
        self,
        payload_file: Path,
        response_text: str | None = None,
        response_file: Path | None = None,
        cited_passage_ids: list[str] | None = None,
    ) -> CharacterChatEvaluationReport:
        """
        从 payload 文件和回答输入生成评估报告。

        @params:
            payload_file: prompt_payload.json 文件路径。
            response_text: 直接传入的角色回答文本。
            response_file: 角色回答文件路径，可为 .txt 或 .json。
            cited_passage_ids: 命令行或调用侧额外传入的证据段落 ID。

        @return:
            结构化评估报告对象。
        """
        payload = self.load_payload(payload_file)
        response_input = self.load_response_input(response_text, response_file, cited_passage_ids or [])
        return self.evaluate(payload, response_input, payload_file)

    def load_payload(self, payload_file: Path) -> dict[str, object]:
        """
        读取 prompt payload JSON 文件。

        @params:
            payload_file: prompt_payload.json 文件路径。

        @return:
            解析后的 payload 字典。
        """
        return json.loads(payload_file.read_text(encoding="utf-8"))

    def load_response_input(
        self,
        response_text: str | None,
        response_file: Path | None,
        cited_passage_ids: list[str],
    ) -> CharacterChatResponseInput:
        """
        解析待评估回答输入。

        @params:
            response_text: 直接传入的角色回答文本。
            response_file: 角色回答文件路径。
            cited_passage_ids: 调用侧额外传入的证据段落 ID。

        @return:
            结构化回答输入对象。
        """
        if response_text and response_file:
            raise ValueError("response_text and response_file cannot be used together.")
        if not response_text and not response_file:
            raise ValueError("Either response_text or response_file must be provided.")

        file_citations: list[str] = []
        source = "inline"
        resolved_response_text = response_text or ""

        if response_file:
            source = str(response_file)
            if response_file.suffix.lower() == ".json":
                payload = json.loads(response_file.read_text(encoding="utf-8"))
                resolved_response_text = self.extract_response_text_from_json(payload)
                file_citations = self.extract_citations_from_json(payload)
            else:
                resolved_response_text = response_file.read_text(encoding="utf-8")

        merged_citations = self.unique_preserving_order(
            [
                *file_citations,
                *cited_passage_ids,
                *self.extract_inline_passage_ids(resolved_response_text),
            ]
        )

        return CharacterChatResponseInput(
            response_text=resolved_response_text.strip(),
            cited_passage_ids=merged_citations,
            response_source=source,
        )

    def extract_response_text_from_json(self, payload: dict[str, object]) -> str:
        """
        从结构化回答 JSON 中提取角色回答正文。

        @params:
            payload: 回答 JSON 对象。

        @return:
            角色回答正文。
        """
        for key in ("assistant_response", "response", "answer", "content"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value
        raise ValueError("Response json must contain assistant_response, response, answer, or content.")

    def extract_citations_from_json(self, payload: dict[str, object]) -> list[str]:
        """
        从结构化回答 JSON 中提取显式证据引用。

        @params:
            payload: 回答 JSON 对象。

        @return:
            证据段落 ID 列表。
        """
        cited_passage_ids = payload.get("cited_passage_ids", [])
        if isinstance(cited_passage_ids, list):
            return [str(item) for item in cited_passage_ids if str(item).strip()]
        return []

    def evaluate(
        self,
        prompt_payload: dict[str, object],
        response_input: CharacterChatResponseInput,
        payload_file: Path,
    ) -> CharacterChatEvaluationReport:
        """
        基于 prompt payload 和角色回答生成评估报告。

        @params:
            prompt_payload: prompt payload 字典。
            response_input: 结构化角色回答输入。
            payload_file: prompt payload 文件路径。

        @return:
            结构化评估报告对象。
        """
        character = prompt_payload["character"]
        user_query = str(prompt_payload["user_query"])
        query_terms = [str(item) for item in prompt_payload.get("query_terms", [])]
        retrieval = prompt_payload["context"]["retrieval"]
        valid_passage_ids = self.collect_retrieval_passage_ids(retrieval)

        auto_checks = {
            "response_nonempty": bool(response_input.response_text),
            "response_length_chars": len(response_input.response_text),
            "query_term_hits": [term for term in query_terms if term and term in response_input.response_text],
            "query_term_miss_count": len([term for term in query_terms if term and term not in response_input.response_text]),
            "retrieval_passage_count": len(valid_passage_ids),
            "cited_passage_ids": response_input.cited_passage_ids,
            "valid_citations": [item for item in response_input.cited_passage_ids if item in valid_passage_ids],
            "invalid_citations": [item for item in response_input.cited_passage_ids if item not in valid_passage_ids],
            "modern_expression_hits": [term for term in self.MODERN_EXPRESSION_TERMS if term in response_input.response_text],
            "uncertainty_hits": [term for term in self.UNCERTAINTY_TERMS if term in response_input.response_text],
            "contains_character_name": str(character["name"]) in response_input.response_text,
        }

        return CharacterChatEvaluationReport(
            status="pending_manual_review",
            generated_at=datetime.now().astimezone().isoformat(timespec="seconds"),
            character_id=str(character["id"]),
            character_name=str(character["name"]),
            user_query=user_query,
            response=response_input,
            auto_checks=auto_checks,
            manual_rubric=self.build_manual_rubric(),
            reviewer_guidance=self.build_reviewer_guidance(),
            source_files={
                "prompt_payload": str(payload_file),
                "response_source": response_input.response_source,
            },
        )

    def collect_retrieval_passage_ids(self, retrieval: dict[str, object]) -> list[str]:
        """
        从检索结果中汇总可接受的证据段落 ID。

        @params:
            retrieval: payload 中的检索结果字典。

        @return:
            去重后的证据段落 ID 列表。
        """
        passage_ids: list[str] = []
        for key in ("style_evidence", "fact_evidence"):
            evidence_items = retrieval.get(key, [])
            if isinstance(evidence_items, list):
                for item in evidence_items:
                    if isinstance(item, dict) and item.get("passage_id"):
                        passage_ids.append(str(item["passage_id"]))
        return self.unique_preserving_order(passage_ids)

    def extract_inline_passage_ids(self, response_text: str) -> list[str]:
        """
        从回答正文中提取形如 passage_000123 的内联证据 ID。

        @params:
            response_text: 角色回答正文。

        @return:
            按出现顺序去重后的 passage_id 列表。
        """
        return self.unique_preserving_order(re.findall(r"passage_\d{6}", response_text))

    def build_manual_rubric(self) -> dict[str, object]:
        """
        构建人工待填评分表。

        @params:
            无。

        @return:
            人工评分项字典。
        """
        rubric: dict[str, object] = {}
        for key, question in self.MANUAL_RUBRIC_ITEMS.items():
            rubric[key] = {
                "question": question,
                "score": None,
                "scale": "1-5",
                "note": "",
            }
        return rubric

    def build_reviewer_guidance(self) -> list[str]:
        """
        返回人工评审时的操作提示。

        @params:
            无。

        @return:
            评审提示列表。
        """
        return [
            "先看 automatic checks，再决定是否需要回查 prompt payload 中的证据段落。",
            "若回答引用了 passage_id，优先核对该引用是否来自当前检索结果。",
            "若回答出现明显现代表达，不必直接判零，但应在 not_modernized 中说明影响。",
            "若回答主动说明证据不足，可在 grounded_in_evidence 中酌情加分。",
        ]

    def unique_preserving_order(self, items: list[str]) -> list[str]:
        """
        对字符串列表去重并保持原有顺序。

        @params:
            items: 待处理字符串列表。

        @return:
            去重后的字符串列表。
        """
        seen: set[str] = set()
        result: list[str] = []
        for item in items:
            if item and item not in seen:
                seen.add(item)
                result.append(item)
        return result
