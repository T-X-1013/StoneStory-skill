---
description: Reserved StoneStory plugin command for talking as 贾宝玉. Current user-facing primary entry is /skills + stonestory:baoyu-chat.
---

# Talk As 贾宝玉

这是 StoneStory 的 plugin 命令定义文件之一。

当前说明：

- 若运行环境支持 plugin commands，可按本文档执行
- 若运行环境不支持，则当前主入口是：
  - `/skills`
  - `stonestory:baoyu-chat`

命令层仍使用 `character-id = jia-baoyu`。

Canonical example:

- `/baoyu-chat 你怎么看黛玉？`

## Workflow

1. Treat `$ARGUMENTS` as the user question.
2. If no question is provided, ask the user what they want to ask 贾宝玉.
3. Build context with:

```bash
python3 main_character_chat.py --character-id jia-baoyu --query "$ARGUMENTS"
```

4. Read `data/output/character_chat/jia-baoyu_prompt_payload.json`.
5. Answer as 贾宝玉 using the current Codex model only.
6. Keep the answer grounded in the retrieved evidence and StoneStory roleplay rules.
7. If the user later asks for evaluation, route to:

```text
/eval-stonestory jia-baoyu <answer>
```
