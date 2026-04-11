# 人物对话模块实现说明

## 1. 文档定位

本文档说明 `StoneStory-skill` 当前已经落地的人物对话前四个模块。

本文档关注：

- 已完成哪些模块
- 每个模块的职责、代码位置与产物
- 当前整体能力边界是什么

本文档不负责：

- 展开未来阶段的路线规划
- 代替评估模块专题文档
- 代替人物回答生成设计文档

相关文档：

- 路线图：`docs/character-chat-plan.md`
- 评估模块：`docs/character-chat-eval.md`
- 回答生成设计：`docs/character-reply-generation.md`
- 人物资产生成：`docs/character-skill-builder.md`

## 2. 当前实现概览

当前已经落地的四个模块是：

1. 人物对话检索编排
2. `style_evidence.jsonl` 质量增强
3. `style.md` 证据化
4. 对话质量评估

这四个模块共同构成了当前的人物对话 baseline：

- 人物资产可生成
- 上下文可构造
- 风格约束可回溯
- 回答可评估

当前尚未落地的是正式的人物回答生成模块。

## 3. 模块一：人物对话检索编排

### 3.1 目标

建立最小可运行的人物对话上下文准备链路。

### 3.2 代码位置

- `main_character_chat.py`
- `tools/characterchat/retriever.py`
- `tools/characterchat/prompt_builder.py`
- `tools/characterchat/cli.py`

### 3.3 输入依赖

该模块会读取人物目录中的下列资产：

- `manifest.json`
- `persona.md`
- `style.md`
- `boundaries.md`
- `relations.md`
- `style_evidence.jsonl`
- `evidence_ranked.jsonl`
- `source_report.json`

### 3.4 实现方式

当前链路分成两层：

- 检索器
- prompt 组装器

检索器负责：

1. 解析人物基础信息
2. 从用户问题中提取检索词
3. 优先检索风格证据
4. 再补充事实证据与关系信息

组装器负责：

- 统一输出 `prompt_payload.json`

### 3.5 当前产物

- `data/output/character_chat/<character-id>_prompt_payload.json`

该文件主要包含：

- `character`
- `user_query`
- `query_terms`
- `constraints`
- `retrieval`
- `generation_requirements`
- `messages`

## 4. 模块二：`style_evidence.jsonl` 质量增强

### 4.1 目标

让风格证据更接近“目标人物确实在说话”的段落集合。

### 4.2 代码位置

- `tools/characterskill/builder.py`

### 4.3 实现方式

当前第一版采用规则驱动，而不是模型或 embedding。

当前重点规则包括：

- 识别目标人物是否为明确说话人
- 对非目标说话人段落降权
- 对多说话人候选段落降权
- 对泛指说话人场景标记噪声类型

### 4.4 当前噪声类型

- `target_not_confirmed_as_speaker`
- `multiple_speaker_candidates`
- `generic_speaker_context`

### 4.5 当前产物

- 更新后的 `style_evidence.jsonl`
- 更新后的 `source_report.json`

## 5. 模块三：`style.md` 证据化

### 5.1 目标

把 `style.md` 从说明性文件升级成带证据支撑的正式风格资产。

### 5.2 代码位置

- `tools/characterskill/models.py`
- `tools/characterskill/builder.py`

### 5.3 实现方式

当前先生成结构化中间层，再由其产出 `style.md`。

中间层文件是：

- `style_summary_candidates.json`

每条候选结论当前包含：

- `trait`
- `title`
- `description`
- `rationale`
- `evidence_passage_ids`
- `evidence_chapter_ids`
- `signal_count`

### 5.4 当前产物

- `style_summary_candidates.json`
- 基于候选结论整理的 `style.md`

## 6. 模块四：对话质量评估

### 6.1 目标

建立一个最小可持续的回答评估机制。

### 6.2 代码位置

- `main_character_eval.py`
- `tools/charactereval/models.py`
- `tools/charactereval/evaluator.py`
- `tools/charactereval/cli.py`

### 6.3 实现方式

当前第一版只做两层能力：

- 自动风险信号收集
- 人工 rubric 预填

它当前不是自动裁判器，而是结构化评估工具。

### 6.4 当前输入输出

输入：

- `prompt_payload.json`
- 回答字符串
- 回答文件

输出：

- `evaluation_report.json`

自动信号当前主要覆盖：

- 回答是否为空
- 回答长度
- query terms 命中情况
- `passage_id` 引用情况
- 现代表达风险
- 保守性表达情况

## 7. 四个模块之间的关系

当前链路关系如下：

1. 先由人物资产生成工具产出人物资产
2. 继续增强 `style_evidence.jsonl`
3. 由证据候选生成 `style.md`
4. 由对话检索编排工具生成 `prompt_payload.json`
5. 由评估模块对回答产出 `evaluation_report.json`

这意味着当前系统已经具备：

- 资产层
- 上下文层
- 评估层

但还没有真正的回答生成层。

## 8. 当前边界

当前已经具备：

- 人物对话最小上下文构造能力
- 第一版风格证据去噪
- 第一版证据化风格资产
- 第一版结构化评估链路

当前尚不具备：

- 正式的人物回答生成模块
- 自动化优劣裁判
- 多轮状态管理
- 服务化入口
