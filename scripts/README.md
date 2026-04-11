# scripts 目录说明

本文档说明 `StoneStory-skill/scripts/` 目录中的本地脚本是做什么的，以及它们和 `/skills` 入口之间的关系。

## 1. 目录定位

`scripts/` 目录中的文件不是 StoneStory 的主对话入口。

它们的定位是：

- 本地调试辅助脚本
- 底层链路验证脚本
- 命令行快捷包装层

当前面向使用者的主入口仍然是：

- 在 Codex 中输入 `/skills`
- 选择 `stonestory:baoyu-chat`
- 选择 `stonestory:daiyu-chat`
- 或选择 `stonestory:stonestory-roleplay`

## 2. 为什么还有这些脚本

虽然当前主入口是 skill，但本地脚本仍然有价值。

它们主要用于：

- 手动生成 `prompt_payload.json`
- 手动执行回答评估
- 不进入 skill 对话时，直接验证底层 Python 工具是否正常
- 排查人物证据、上下文构造和评估链路的问题

可以把它们理解为：

- 对 `main_character_chat.py` 和 `main_character_eval.py` 的一层薄包装

## 3. 当前有哪些脚本

当前目录中有四个脚本：

- `stonestory-chat`
- `baoyu-chat`
- `daiyu-chat`
- `stonestory-eval`

## 4. 每个脚本的作用

### 4.1 `stonestory-chat`

作用：

- 通用的人物对话上下文构造脚本

用法：

```bash
scripts/stonestory-chat <character-id> <question>
```

示例：

```bash
scripts/stonestory-chat jia-baoyu "你怎么看黛玉？"
scripts/stonestory-chat lin-daiyu "你怎么看宝玉？"
```

它实际调用的是：

```bash
python3 main_character_chat.py --character-id <character-id> --query "<question>"
```

输出结果通常是：

- `data/output/character_chat/<character-id>_prompt_payload.json`

### 4.2 `baoyu-chat`

作用：

- 贾宝玉专用快捷脚本

用法：

```bash
scripts/baoyu-chat <question>
```

示例：

```bash
scripts/baoyu-chat "你怎么看黛玉？"
```

它本质上等价于：

```bash
scripts/stonestory-chat jia-baoyu "<question>"
```

### 4.3 `daiyu-chat`

作用：

- 林黛玉专用快捷脚本

用法：

```bash
scripts/daiyu-chat <question>
```

示例：

```bash
scripts/daiyu-chat "你怎么看宝玉？"
```

它本质上等价于：

```bash
scripts/stonestory-chat lin-daiyu "<question>"
```

### 4.4 `stonestory-eval`

作用：

- 对一段人物回答执行结构化评估

用法：

```bash
scripts/stonestory-eval <character-id> <answer>
```

示例：

```bash
scripts/stonestory-eval jia-baoyu "妹妹自然是极好的人。[passage_001716]"
scripts/stonestory-eval lin-daiyu "我也未敢定论。[passage_000256]"
```

它实际调用的是：

```bash
python3 main_character_eval.py --payload data/output/character_chat/<character-id>_prompt_payload.json --response "<answer>"
```

注意：

- 运行这个脚本前，应先存在对应人物的 `prompt_payload.json`
- 若文件不存在，应先运行 `scripts/stonestory-chat` 或对应人物快捷脚本

## 5. 与 `/skills` 的关系

两者的关系可以这样理解：

- `/skills`
  - 面向使用者
  - 用于直接发起人物对话
- `scripts/`
  - 面向开发和调试
  - 用于手动构造上下文与手动执行评估

因此，普通对话时优先使用 `/skills`。

只有在下面这些场景，才优先使用本地脚本：

- 调试底层链路
- 手动检查 `prompt_payload.json`
- 不经过 skill，直接验证上下文构造结果
- 对某段回答单独执行评估

## 6. 当前建议

如果你的目标是“直接和人物对话”，优先使用：

- `/skills`

如果你的目标是“检查底层文件和链路”，优先使用：

- `scripts/stonestory-chat`
- `scripts/baoyu-chat`
- `scripts/daiyu-chat`
- `scripts/stonestory-eval`
