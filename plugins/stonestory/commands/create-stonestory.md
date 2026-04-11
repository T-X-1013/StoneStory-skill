---
description: Reserved StoneStory plugin command for starting the shared roleplay workflow. Current user-facing primary entry is /skills + stonestory:stonestory-roleplay.
---

# Create StoneStory Session

这是 StoneStory 的共享 plugin 命令定义文件。

当前说明：

- 若运行环境支持 plugin commands，可按本文档执行
- 若运行环境不支持，则当前主入口是：
  - `/skills`
  - `stonestory:stonestory-roleplay`

该命令不调用外部模型 API，只复用本地 StoneStory 资产与 Python 工具。

## Arguments

Interpret `$ARGUMENTS` as either:

- empty: enter StoneStory workflow mode and ask the user which character and question to use
- `<character-id> <question>`: directly prepare context for that character and question

Canonical examples:

- `/create-stonestory jia-baoyu 你怎么看黛玉？`
- `/create-stonestory lin-daiyu 你怎么看宝玉？`

Supported `character-id` values in the current repo:

- `jia-baoyu`
- `lin-daiyu`

## Workflow

1. Confirm the repo root is `/Users/tao/PyCharmProject/StoneStory-skill` or the current repo root when this plugin is used locally.
2. If arguments are empty, ask the user which character and question to use.
3. If arguments are present, parse:
   - the first token as `character-id`
   - the remaining text as the user question
4. Run the existing StoneStory context builder:

```bash
python3 main_character_chat.py --character-id <character-id> --query "<question>"
```

5. Read the generated prompt payload:

- `data/output/character_chat/<character-id>_prompt_payload.json`

6. Use the current Codex model to answer in-character while following:
   - retrieved evidence
   - `persona.md`
   - `style.md`
   - `boundaries.md`
   - `style_summary_candidates.json`

7. If the user asks for evaluation, run:

```bash
python3 main_character_eval.py --payload data/output/character_chat/<character-id>_prompt_payload.json --response "<answer>"
```

## Rules

- Do not use any external model API.
- Use Codex itself as the runtime model.
- Do not invent facts not supported by retrieved evidence.
- If evidence is insufficient, say so explicitly.
- Keep the answer within the Hongloumeng setting and avoid modern slang.
- Before answering, confirm the payload file exists and is the latest output for the requested character.
- After answering, if the user asks for grading or verification, route to `/eval-stonestory` when command mode is available, otherwise use the local evaluation workflow.
