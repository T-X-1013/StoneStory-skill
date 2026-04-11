# StoneStory 本地脚本说明

## 1. 文档定位

本文档说明 StoneStory 的本地脚本工具。

本文档关注：

- 哪些脚本可以直接运行
- 每条脚本接收什么输入
- 每条脚本会产出什么文件

本文档不负责：

- skill 对话入口说明
- plugin 目录结构说明

这些脚本的定位是：

- 开发调试
- 手动构造 `prompt_payload.json`
- 手动执行回答评估

它们不是当前面向使用者的主对话入口。

## 2. 当前可用脚本

当前提供四个脚本：

- [stonestory-chat](/Users/tao/PyCharmProject/StoneStory-skill/scripts/stonestory-chat)
- [baoyu-chat](/Users/tao/PyCharmProject/StoneStory-skill/scripts/baoyu-chat)
- [daiyu-chat](/Users/tao/PyCharmProject/StoneStory-skill/scripts/daiyu-chat)
- [stonestory-eval](/Users/tao/PyCharmProject/StoneStory-skill/scripts/stonestory-eval)

进入项目目录后使用：

```bash
cd /Users/tao/PyCharmProject/StoneStory-skill
```

## 3. 对话上下文构造

这一部分的作用是手动生成人物对话上下文文件，供调试、检查或评估使用。

### 3.1 通用命令

```bash
bash scripts/stonestory-chat jia-baoyu "你怎么看黛玉？"
bash scripts/stonestory-chat lin-daiyu "你怎么看宝玉？"
```

输入：

- `character_id`
- 用户问题

输出：

- `data/output/character_chat/<character-id>_prompt_payload.json`

### 3.2 贾宝玉快捷命令

```bash
bash scripts/baoyu-chat "你怎么看黛玉？"
```

输出：

- `data/output/character_chat/jia-baoyu_prompt_payload.json`

### 3.3 林黛玉快捷命令

```bash
bash scripts/daiyu-chat "你怎么看宝玉？"
```

输出：

- `data/output/character_chat/lin-daiyu_prompt_payload.json`

## 4. 回答评估

先确保对应人物的 `prompt_payload.json` 已生成，再运行：

```bash
bash scripts/stonestory-eval jia-baoyu "妹妹自然是极好的人。[passage_001716]"
bash scripts/stonestory-eval lin-daiyu "我也未敢定论。[passage_000256]"
```

输入：

- `character_id`
- 一段人物回答

输出：

- `data/eval/<character-id>_prompt_payload_evaluation.json`

## 5. 与 skill 对话入口的关系

当前面向使用者的主入口是：

- `/skills`
- `stonestory:baoyu-chat`
- `stonestory:daiyu-chat`
- `stonestory:stonestory-roleplay`

本地脚本更适合下面这些场景：

- 需要手动检查 `prompt_payload.json`
- 需要离线调试检索与组装结果
- 需要对某段回答单独执行评估
- 需要在不进入 skill 对话的情况下验证底层链路

skill 对话入口见：

- [stonestory-skill-chat.md](/Users/tao/PyCharmProject/StoneStory-skill/docs/stonestory-skill-chat.md)
