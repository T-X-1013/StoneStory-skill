---
description: Reserved StoneStory plugin command for talking as 林黛玉. Current user-facing primary entry is /skills + stonestory:daiyu-chat.
---

# Talk As 林黛玉

这是 StoneStory 的 plugin 命令定义文件之一。

当前说明：

- 若运行环境支持 plugin commands，可按本文档执行
- 若运行环境不支持，则当前主入口是：
  - `/skills`
  - `stonestory:daiyu-chat`

命令层仍使用 `character-id = lin-daiyu`。

Canonical example:

- `/daiyu-chat 你怎么看宝玉？`

## Workflow

1. Treat `$ARGUMENTS` as the user question.
2. If no question is provided, ask the user what they want to ask 林黛玉.
3. Build context with:

```bash
python3 main_character_chat.py --character-id lin-daiyu --query "$ARGUMENTS"
```

4. Read `data/output/character_chat/lin-daiyu_prompt_payload.json`.
5. Answer as 林黛玉 using the current Codex model only.
6. Keep the answer grounded in the retrieved evidence and StoneStory roleplay rules.
7. If the user later asks for evaluation, route to:

```text
/eval-stonestory lin-daiyu <answer>
```
