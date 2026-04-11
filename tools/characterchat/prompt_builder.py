"""
人物对话 prompt 组装器

支持格式：
1. 人物检索结果字典

输出：
1. prompt_payload.json 对应的数据结构
2. 可供模型直接使用的 messages 数组

用法：
    from tools.characterchat.prompt_builder import CharacterChatPromptBuilder

    builder = CharacterChatPromptBuilder()
    payload = builder.build_prompt_payload(retrieval_result)
"""

from __future__ import annotations


class CharacterChatPromptBuilder:
    """把人物检索结果组装为第一版 prompt payload。"""

    def build_prompt_payload(self, retrieval_result: dict[str, object]) -> dict[str, object]:
        """
        将检索结果转换为结构化 prompt payload。

        @params:
            retrieval_result: 人物检索结果字典。

        @return:
            prompt payload 字典，包含消息数组、上下文与检索结果摘要。
        """
        character = retrieval_result["character"]
        constraints = retrieval_result["constraints"]
        retrieval = retrieval_result["retrieval"]
        user_query = str(retrieval_result["user_query"])
        query_terms = list(retrieval_result["query_terms"])

        system_prompt = self.compose_system_prompt(character, constraints, retrieval)
        user_prompt = self.compose_user_prompt(user_query, query_terms)

        return {
            "character": character,
            "user_query": user_query,
            "query_terms": query_terms,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "context": {
                "constraints": constraints,
                "retrieval": retrieval,
            },
            "generation_requirements": [
                "保持角色身份和时代语境，不使用现代网络表达。",
                "优先依据已检索到的原文证据回答，不得伪造原著事实。",
                "若证据不足，应明确说明不能确定，而不是强行补写。",
            ],
        }

    def compose_system_prompt(
        self,
        character: dict[str, object],
        constraints: dict[str, object],
        retrieval: dict[str, object],
    ) -> str:
        """
        拼接系统消息内容。

        @params:
            character: 人物基础信息。
            constraints: 人物约束文档内容。
            retrieval: 检索结果摘要。

        @return:
            系统消息字符串。
        """
        sections = [
            f"你现在扮演《红楼梦》人物：{character['name']}（character_id={character['id']}）。",
            "",
            "请严格遵守以下人物资产与回答边界：",
            "",
            "【Persona】",
            str(constraints["persona_markdown"]),
            "",
            "【Style】",
            str(constraints["style_markdown"]),
            "",
            "【Boundaries】",
            str(constraints["boundaries_markdown"]),
            "",
            "【Relevant Relations】",
            self.format_relations(retrieval["relations"]),
            "",
            "【Style Evidence】",
            self.format_evidence(retrieval["style_evidence"]),
            "",
            "【Fact Evidence】",
            self.format_evidence(retrieval["fact_evidence"]),
            "",
            "回答要求：",
            "1. 尽量使用角色口吻，但不要伪造原著没有的事实。",
            "2. 当证据不足时，要明确说明不能确定。",
            "3. 回答时优先围绕已提供证据，不要脱离《红楼梦》语境。",
        ]
        return "\n".join(sections)

    def compose_user_prompt(self, user_query: str, query_terms: list[str]) -> str:
        """
        拼接用户消息内容。

        @params:
            user_query: 用户问题。
            query_terms: 检索关键词列表。

        @return:
            用户消息字符串。
        """
        if query_terms:
            return f"用户问题：{user_query}\n检索关键词：{', '.join(query_terms)}"
        return f"用户问题：{user_query}"

    def format_relations(self, relations: list[dict[str, object]]) -> str:
        """
        将关系列表格式化为 prompt 中的可读文本。

        @params:
            relations: 关系字典列表。

        @return:
            格式化后的多行字符串。
        """
        if not relations:
            return "- 无相关关系上下文。"
        return "\n".join(
            f"- {item['head']} -- {item['relation']}（{item['label']}）--> {item['tail']}" for item in relations
        )

    def format_evidence(self, evidence: list[dict[str, object]]) -> str:
        """
        将证据列表格式化为 prompt 中的可读文本。

        @params:
            evidence: 证据字典列表。

        @return:
            格式化后的多行字符串。
        """
        if not evidence:
            return "- 无检索证据。"

        lines: list[str] = []
        for item in evidence:
            lines.append(
                f"- [{item['chapter_id']} / {item['passage_id']}] "
                f"score={item.get('retrieval_score', item.get('score', 0))} "
                f"text={item['text']}"
            )
        return "\n".join(lines)
