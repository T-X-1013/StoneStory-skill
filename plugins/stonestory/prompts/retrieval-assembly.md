# Retrieval Assembly Template

在回答前，应优先检查：

1. 是否已有 `prompt_payload.json`
2. `style_evidence` 是否足够支持角色口吻
3. `fact_evidence` 是否足够支持事实判断
4. `relations` 是否和当前问题相关

若 payload 不存在，应先运行：

```bash
python3 main_character_chat.py --character-id <character-id> --query "<question>"
```
