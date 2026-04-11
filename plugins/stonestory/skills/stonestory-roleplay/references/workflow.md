# Workflow

StoneStory plugin 的最小工作流如下：

1. 接收角色和用户问题
2. 调用本地上下文构造工具
3. 读取 `prompt_payload.json`
4. 用 Codex 当前模型生成角色回答
5. 如用户要求，调用本地评估工具生成 `evaluation_report.json`

对应本地命令：

```bash
python3 main_character_chat.py --character-id <character-id> --query "<question>"
python3 main_character_eval.py --payload data/output/character_chat/<character-id>_prompt_payload.json --response "<answer>"
```
