"""
人物对话评估数据模型

支持格式：
1. prompt_payload.json
2. .txt 角色回答文件
3. .json 角色回答文件

输出：
1. 角色回答输入模型
2. 角色回答评估报告模型

用法：
    from tools.charactereval.models import CharacterChatResponseInput, CharacterChatEvaluationReport
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterChatResponseInput:
    """表示一次待评估的角色回答输入。"""

    response_text: str          # 角色回答正文。
    cited_passage_ids: list[str]  # 回答中显式给出的证据段落 ID。
    response_source: str        # 回答来源路径或 inline 标记。

    def to_dict(self) -> dict[str, object]:
        """
        将回答输入转换为可直接写入 JSON 的字典结构。

        @params:
            无。

        @return:
            包含回答正文、证据 ID 和来源的字典对象。
        """
        return {
            "response_text": self.response_text,
            "cited_passage_ids": self.cited_passage_ids,
            "response_source": self.response_source,
        }


@dataclass(frozen=True)
class CharacterChatEvaluationReport:
    """表示一次角色回答评估的完整报告。"""

    status: str                           # 当前报告状态，例如 pending_manual_review。
    generated_at: str                     # 报告生成时间。
    character_id: str                     # 角色唯一 ID。
    character_name: str                   # 角色中文名。
    user_query: str                       # 用户问题。
    response: CharacterChatResponseInput  # 待评估回答输入。
    auto_checks: dict[str, object]        # 自动检查得到的结构化信号。
    manual_rubric: dict[str, object]      # 人工待填评分表。
    reviewer_guidance: list[str]          # 评审提示。
    source_files: dict[str, str]          # 本次评估使用的输入文件。

    def to_dict(self) -> dict[str, object]:
        """
        将评估报告转换为可直接写入 JSON 的字典结构。

        @params:
            无。

        @return:
            包含评估报告全部字段的字典对象。
        """
        return {
            "status": self.status,
            "generated_at": self.generated_at,
            "character_id": self.character_id,
            "character_name": self.character_name,
            "user_query": self.user_query,
            "response": self.response.to_dict(),
            "auto_checks": self.auto_checks,
            "manual_rubric": self.manual_rubric,
            "reviewer_guidance": self.reviewer_guidance,
            "source_files": self.source_files,
        }
