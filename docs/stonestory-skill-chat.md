# StoneStory Skill 对话手册

## 1. 文档定位

本文档说明在 Codex 中如何通过 StoneStory skill 发起人物对话。

本文档关注：

- 当前主入口是什么
- 应选择哪个 skill
- 用户该如何开始对话
- skill 模式下默认会发生什么

本文档不负责：

- 本地脚本调试说明
- plugin 目录结构说明
- 人物资产生成细节

## 2. 当前主入口

当前在 Codex 中，StoneStory 面向使用者的主入口是：

- `/skills`

进入后，推荐选择以下 skill：

- `stonestory:baoyu-chat`
- `stonestory:daiyu-chat`
- `stonestory:stonestory-roleplay`

其中：

- `stonestory:baoyu-chat`
  - 直接进入贾宝玉人物对话
- `stonestory:daiyu-chat`
  - 直接进入林黛玉人物对话
- `stonestory:stonestory-roleplay`
  - 作为通用入口，适合先指定人物再继续对话

## 3. 如何开始对话

### 3.1 贾宝玉

在 Codex 中先选择：

- `stonestory:baoyu-chat`

然后直接提问，例如：

```text
你怎么看黛玉？
```

### 3.2 林黛玉

在 Codex 中先选择：

- `stonestory:daiyu-chat`

然后直接提问，例如：

```text
你怎么看宝玉？
```

### 3.3 通用入口

若先进入：

- `stonestory:stonestory-roleplay`

可以先说：

```text
我想和《红楼梦》人物对话。
```

若角色未明确，通用入口会先要求补充角色。

## 4. 默认行为

在 StoneStory 人物 skill 模式下，当前默认行为是：

- 直接输出人物口吻回答
- 默认隐藏中间分析和过程汇报
- 只有在用户明确要求时，才解释证据或推理依据

因此目标输出更接近：

- `jia-baoyu.skill ❯ ...`
- `lin-daiyu.skill ❯ ...`

## 5. 什么时候需要看本地脚本

大多数情况下，普通对话只需要走 skill 入口，不需要关心本地脚本。

只有在下面这些场景，才需要看本地脚本或底层文件：

- 需要手动检查 `prompt_payload.json`
- 需要离线调试人物对话上下文
- 需要单独对某段回答执行评估
- 需要排查证据或引用是否来自底层构造结果

对应说明见：

- [stonestory-terminal-commands.md](/Users/tao/PyCharmProject/StoneStory-skill/docs/stonestory-terminal-commands.md)

## 6. 与本地数据链路的关系

当问题较复杂，或需要更强的原文约束时，StoneStory skill 可以读取本地构造结果，再组织回答。

最常见的本地结果是：

- `data/output/character_chat/<character-id>_prompt_payload.json`

这个文件由底层 Python 工具或本地脚本生成。

## 7. 相关文件

- [baoyu-chat skill](/Users/tao/PyCharmProject/StoneStory-skill/plugins/stonestory/skills/baoyu-chat/SKILL.md)
- [daiyu-chat skill](/Users/tao/PyCharmProject/StoneStory-skill/plugins/stonestory/skills/daiyu-chat/SKILL.md)
- [stonestory-roleplay skill](/Users/tao/PyCharmProject/StoneStory-skill/plugins/stonestory/skills/stonestory-roleplay/SKILL.md)
- [stonestory-plugin-layout.md](/Users/tao/PyCharmProject/StoneStory-skill/docs/stonestory-plugin-layout.md)
- [stonestory-terminal-commands.md](/Users/tao/PyCharmProject/StoneStory-skill/docs/stonestory-terminal-commands.md)
