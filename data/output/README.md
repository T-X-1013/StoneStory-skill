# data/output 目录说明

本文档说明 `StoneStory-skill/data/output/` 目录中当前各个文件和子目录的作用、生成步骤，以及 `character_chat/*.json` 中各字段的含义。

## 1. 目录总览

当前 `data/output/` 下主要包含：

- `chapters.json`
- `passages.jsonl`
- `build_report.json`
- `character_chat/`

它们分别来自两条不同链路：

1. 基础数据构建链路
   - 入口：`python3 main.py`
   - 代码：`tools/databuilder/`
2. 人物对话上下文构造链路
   - 入口：`python3 main_character_chat.py`
   - 代码：`tools/characterchat/`

## 2. 每个文件是什么，由哪一步生成

### 2.1 `chapters.json`

作用：

- 保存全书章节级结构化数据
- 为后续检索、章节定位、摘要生成提供章节元信息

生成步骤：

- 由基础数据构建链路生成
- 命令入口：`python3 main.py`

来源输入：

- `data/input/StoneStory.txt`
- 参考报告文件：
  - `data/input/chapters_detected.json`
  - `data/input/quality_report.json`
  - `data/input/suspicious_char_report.json`

### 2.2 `passages.jsonl`

作用：

- 保存全书段落级结构化数据
- 作为人物证据抽取、原文检索、引用定位的基础数据源

生成步骤：

- 由基础数据构建链路生成
- 命令入口：`python3 main.py`

来源输入：

- `data/input/StoneStory.txt`

### 2.3 `build_report.json`

作用：

- 保存本次数据构建后的校验结果
- 记录章节数量、段落数量、错误数、警告数和异常项明细

生成步骤：

- 由基础数据构建链路生成
- 命令入口：`python3 main.py`

来源输入：

- 当前构建结果
- `data/input/quality_report.json`
- `data/input/chapters_detected.json`
- `data/input/suspicious_char_report.json`

### 2.4 `character_chat/`

作用：

- 保存人物对话上下文构造结果
- 为后续人物回答提供统一的 `prompt_payload.json`

当前目录中已有：

- `jia-baoyu_prompt_payload.json`
- `lin-daiyu_prompt_payload.json`

生成步骤：

- 由人物对话上下文构造链路生成
- 命令入口：
  - `python3 main_character_chat.py --character-id jia-baoyu --query "..."`
  - `python3 main_character_chat.py --character-id lin-daiyu --query "..."`

也可以通过本地脚本间接生成：

- `bash scripts/baoyu-chat "..."`
- `bash scripts/daiyu-chat "..."`

## 3. `character_chat/` 下文件的作用

`character_chat/*.json` 的本质是：

- 一次“人物 + 用户问题”的结构化上下文快照

它不是最终回答结果，而是回答前的准备文件。

它的主要用途是：

- 把人物资产、回答边界、关系信息、证据段落和用户问题统一整理到一个 JSON 中
- 供 Codex skill 或后续回答生成模块直接消费
- 供评估模块回查“这次回答是基于什么上下文产生的”

当前这两个文件虽然人物不同，但字段结构相同。

## 4. `character_chat/*.json` 顶层字段说明

当前 `prompt_payload.json` 顶层主要包含：

- `character`
- `user_query`
- `query_terms`
- `messages`
- `context`
- `generation_requirements`

下面按字段逐层说明。

### 4.1 `character`

作用：

- 记录当前对话对应的人物基础信息

当前子字段包括：

- `id`
  - 人物唯一标识
  - 例如：`jia-baoyu`、`lin-daiyu`
- `name`
  - 人物中文名
  - 例如：`贾宝玉`
- `aliases`
  - 人物别名列表
  - 用于检索和匹配证据
- `skill_dir`
  - 当前人物资产目录相对路径
  - 例如：`skill/characters/jia-baoyu.skill`

### 4.2 `user_query`

作用：

- 保存用户原始问题

示例：

- `你怎么看黛玉？`
- `详细介绍一下你自己，你是谁？`

### 4.3 `query_terms`

作用：

- 保存从用户问题中提取出的检索关键词

说明：

- 这些词会参与证据排序和关系召回
- 若问题里没有稳定可抽取的关键词，该字段可能为空数组

示例：

- `["黛玉"]`
- `[]`

### 4.4 `messages`

作用：

- 保存可直接交给模型的对话消息数组

当前通常包含两条消息：

1. `system`
   - 角色身份、人物资产、边界、关系、证据、回答要求
2. `user`
   - 用户问题和检索关键词摘要

每条消息当前包含：

- `role`
  - 消息角色
  - 当前常见值：`system`、`user`
- `content`
  - 消息正文
  - 对 `system` 来说，是拼接后的完整提示词
  - 对 `user` 来说，是用户问题和检索词摘要

### 4.5 `context`

作用：

- 保存 `messages` 背后的结构化上下文

这是给程序看、给调试看、给评估回查看的主要部分。

当前包含两个子对象：

- `constraints`
- `retrieval`

### 4.6 `generation_requirements`

作用：

- 保存最终回答时必须遵守的生成要求列表

当前每一条都是自然语言约束，例如：

- 保持角色身份和时代语境
- 优先依据已检索证据回答
- 证据不足时明确说明不能确定

这个字段的意义是：

- 给回答层一个更稳定、更简短的最终约束清单

## 5. `context.constraints` 字段说明

`context.constraints` 用于保存三份核心人物约束文档的正文快照。

当前子字段包括：

- `persona_markdown`
- `style_markdown`
- `boundaries_markdown`

### 5.1 `persona_markdown`

作用：

- 保存人物 `persona.md` 的正文

内容特点：

- 以事实和约束为主
- 不写无证据支撑的人物判断

### 5.2 `style_markdown`

作用：

- 保存人物 `style.md` 的正文

内容特点：

- 来自 `style_evidence.jsonl` 和 `style_summary_candidates.json`
- 用于约束人物说话风格和表达倾向

### 5.3 `boundaries_markdown`

作用：

- 保存人物 `boundaries.md` 的正文

内容特点：

- 规定人物回答时不能越过的边界
- 例如不能现代化、不能伪造原文、证据不足时要保守表达

## 6. `context.retrieval` 字段说明

`context.retrieval` 用于保存当前问题检索到的结构化结果。

当前子字段包括：

- `relations`
- `style_evidence`
- `fact_evidence`

### 6.1 `relations`

作用：

- 保存与当前人物最相关的一组关系条目

每条关系对象当前包含：

- `head`
  - 关系头实体
  - 例如：`春纤`
- `relation`
  - 关系类型的内部标识
  - 例如：`servant_girl`
- `label`
  - 关系类型中文标签
  - 例如：`丫鬟`
- `tail`
  - 关系尾实体
  - 当前通常是目标人物
- `score`
  - 当前关系检索分数
  - 第一版里通常为 `0`，主要表示已入选但未做细粒度排序

### 6.2 `style_evidence`

作用：

- 保存更适合支撑人物风格分析的证据段落

这一部分通常优先保留：

- 目标人物明确发话
- 对话上下文清晰
- 与当前用户问题较相关的段落

每条风格证据对象当前包含：

- `character_id`
  - 目标人物 ID
- `character_name`
  - 目标人物中文名
- `chapter_id`
  - 证据所在章节 ID
- `passage_id`
  - 证据段落 ID
- `paragraph_id`
  - 证据段落的章内定位 ID
- `paragraph_no`
  - 段落在所属章节中的顺序号
- `matched_terms`
  - 该段落命中的人物检索词
  - 可能是全名、别名或多个识别词
- `score`
  - 原始风格证据分数
  - 来自人物资产生成阶段
- `signal_type`
  - 当前证据的主信号类型
  - 例如：`speech_marker`
- `signals`
  - 当前段落命中的增强信号列表
  - 例如是否含全名、是否含引语、是否是目标人物直接发话
- `text`
  - 段落正文
- `retrieval_score`
  - 面向当前用户问题再次排序后的分数
  - 用于表示该证据对这次问题的相关程度
- `matched_query_terms`
  - 当前段落命中的用户问题关键词
  - 若未命中，则为空数组

### 6.3 `fact_evidence`

作用：

- 保存更适合支撑事实性回答的证据段落

这一部分和 `style_evidence` 的区别是：

- `style_evidence` 更偏“怎么说”
- `fact_evidence` 更偏“说什么”

每条事实证据对象当前包含：

- `character_id`
  - 目标人物 ID
- `character_name`
  - 目标人物中文名
- `chapter_id`
  - 证据所在章节 ID
- `passage_id`
  - 证据段落 ID
- `paragraph_id`
  - 段落在章内的定位 ID
- `paragraph_no`
  - 段落在所属章节中的顺序号
- `matched_terms`
  - 该段落命中的人物识别词
- `score`
  - 原始证据分数
- `signals`
  - 增强信号列表
- `noise_flags`
  - 噪声标记列表
  - 用于提示该段落虽然可用，但可能存在歧义或质量风险
- `text`
  - 段落正文
- `retrieval_score`
  - 面向当前问题重新排序后的分数
- `matched_query_terms`
  - 当前段落命中的问题关键词

## 7. 字段之间如何理解

可以把 `prompt_payload.json` 简化理解为三层：

1. 顶层元信息
   - `character`、`user_query`、`query_terms`
2. 可直接给模型的消息
   - `messages`
3. 供程序和人回查的结构化上下文
   - `context`
   - `generation_requirements`

也就是说：

- `messages` 负责“拿去回答”
- `context` 负责“解释这份回答上下文是怎么来的”

## 8. 当前目录的使用建议

如果是普通使用者，通常只需要知道：

- `chapters.json`
  - 章节级结构化结果
- `passages.jsonl`
  - 段落级结构化结果
- `character_chat/*.json`
  - 人物对话前的上下文准备结果

如果是开发者或调试者，建议重点关注：

- `build_report.json`
  - 基础构建是否正常
- `character_chat/*.json`
  - 某次人物对话到底读了哪些约束和证据
