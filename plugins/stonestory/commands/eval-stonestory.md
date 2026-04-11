---
description: Reserved StoneStory plugin command for evaluating a reply against the latest prompt payload. Current primary usage may also go through the local evaluation command.
---

# Evaluate StoneStory Reply

这是 StoneStory 的评估命令定义文件。

当前说明：

- 若运行环境支持 plugin commands，可按本文档执行
- 若运行环境不支持，也可以直接使用本地评估命令：

```bash
python3 main_character_eval.py --payload data/output/character_chat/<character-id>_prompt_payload.json --response "<answer>"
```

该命令的作用是生成结构化评估报告。

## Arguments

Interpret `$ARGUMENTS` as:

- `<character-id> <answer>`

Supported `character-id` values:

- `jia-baoyu`
- `lin-daiyu`

Canonical examples:

- `/eval-stonestory jia-baoyu 妹妹自然是极好的人。[passage_001716]`
- `/eval-stonestory lin-daiyu 我也未敢定论。[passage_000256]`

## Workflow

1. Parse the first token as `character-id`.
2. Treat the remaining text as the answer to evaluate.
3. Resolve payload path:

- `data/output/character_chat/<character-id>_prompt_payload.json`

4. Run:

```bash
python3 main_character_eval.py --payload data/output/character_chat/<character-id>_prompt_payload.json --response "<answer>"
```

5. Read and summarize the generated report:

- `data/eval/<character-id>_prompt_payload_evaluation.json`

6. Summarize at least:
   - `valid_citations`
   - `invalid_citations`
   - `modern_expression_hits`
   - `query_term_hits`
   - `manual_rubric`

## Rules

- Preserve the user's answer text exactly when passing it to evaluation.
- Do not rewrite the answer before evaluation.
