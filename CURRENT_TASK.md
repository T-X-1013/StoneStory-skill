# Current Task

## 当前目标

在现有《红楼梦》数据集和人物资产基础上，持续完善 StoneStory 当前的人物对话 baseline。

## 当前重点

- 强化 `jia-baoyu` 和 `lin-daiyu` 的证据约束型角色对话
- 保持人物对话流程以本地资产和 Codex 为核心
- 继续区分：
  - 离线数据构建
  - 人物资产生成
  - 人物对话上下文构造
  - 人物回答评估
  - Codex plugin / skill 入口

## 当前输入

- `data/input/StoneStory.txt`
- `data/output/chapters.json`
- `data/output/passages.jsonl`
- `data/input/triples.csv`
- `skill/characters/jia-baoyu.skill/`
- `skill/characters/lin-daiyu.skill/`

## 当前输出

- `data/output/character_chat/<character_id>_prompt_payload.json`
- `data/eval/<character_id>_prompt_payload_evaluation.json`
- 基于证据的人物资产文件
- 面向 Codex 的 StoneStory plugin / skill 文件

## 当前状态

当前已经具备：

- 基础数据构建链路
- 人物 Skill 资产生成链路
- 人物对话上下文构造链路
- 人物回答评估链路
- 通过 `/skills` 进入的人物对话入口

当前仍缺：

- 独立的人物回答生成代码层
- 稳定的多轮状态管理
- 更完整的回答版本对比与自动评估能力

## 当前要求

- 人物回答应尽量建立在本地 evidence 之上
- 不静默补写缺少证据支持的事实
- 优先使用 UTF-8 与本地 JSON / JSONL 资产
- StoneStory 对话行为应与普通 Codex 对话隔离
- 在人物 skill 模式下，默认输出最终角色回答，而不是中间过程说明
