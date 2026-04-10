# 数据构建模块设计文档

## 1. 文档定位

本文档定义 `StoneStory-skill` 中《红楼梦》基础数据构建模块的设计目标、输入输出约定、切分规则、数据模型与后续演进方向。

本文档关注的是“数据如何被构建出来”，不负责说明：

- skill 运行时如何消费这些数据
- 角色对话逻辑如何实现
- 问答推理链路如何编排

## 2. 背景与目标

本项目第一版围绕《红楼梦》构建开源 skill，重点能力包括：

- 知识问答
- 角色对话
- 原文检索与章节定位
- 结构化数据构建

为了支撑这些能力，需要先建立一个稳定、可追踪、便于扩展的通用知识底座。

本模块当前目标：

- 从清洗后的《红楼梦》txt 中准确切分出 120 回章节
- 在章节内部完成稳定的段落切分
- 生成章节级与段落级结构化数据
- 为后续摘要、关系抽取、事件抽取、引用定位提供统一 ID 体系

## 3. 范围与边界

当前版本负责：

- 读取 UTF-8 编码的清洗文本
- 识别章节标题
- 生成 `chapters.json`
- 生成 `passages.jsonl`

当前版本不负责：

- 自动修复可疑字符
- 人物、地点、事件、关系抽取
- 引文去重与名句标注
- 检索索引建立
- 向量化或 embedding 处理

## 4. 输入与输出规范

### 4.1 输入

当前输入文件：

- `data/input/StoneStory.txt`
- `data/input/chapters_detected.json`
- `data/input/suspicious_char_report.json`
- `data/input/quality_report.json`

输入要求：

- 文件编码必须为 UTF-8
- 文本已完成基础清洗
- 章节标题保留 `第...回` 格式
- 段落之间存在可识别的空行分隔

### 4.2 输出

当前输出文件：

- `data/output/chapters.json`
- `data/output/passages.jsonl`
- `data/output/build_report.json`

输出要求：

- 文件编码统一为 UTF-8
- `chapters.json` 使用 JSON 数组格式
- `passages.jsonl` 使用 JSON Lines 格式，一行一个对象
- `build_report.json` 输出本次构建后的校验报告
- 输出字段应保持稳定，后续新增字段尽量向后兼容

## 5. 模块职责与目录位置

当前数据构建工具代码位于：

- `tools/databuilder`

当前技能资产目录位于：

- `skill/`

目录分工如下：

- `tools/databuilder`：离线数据构建程序
- `docs/`：设计说明与技术文档
- `skill/`：供 skill 使用的 Markdown、角色配置、Prompt 与知识资产
- `data/output/`：结构化输出结果

## 6. 数据模型

### 6.1 Chapter 模型

`chapters.json` 中每个对象表示一个章节。

示例：

```json
{
  "chapter_id": "chapter_001",
  "chapter_no": 1,
  "chapter_label": "第一回",
  "title": "甄士隐梦幻识通灵 贾雨村风尘怀闺秀",
  "paragraph_count": 40,
  "source_text_length": 7510
}
```

字段定义：

- `chapter_id`
  - 类型：`string`
  - 含义：章节唯一 ID
  - 约束：格式固定为 `chapter_001` 这类三位补零编号

- `chapter_no`
  - 类型：`integer`
  - 含义：章节阿拉伯数字序号
  - 约束：应与 `chapter_label` 保持一致，第一回为 `1`，第一百二十回为 `120`

- `chapter_label`
  - 类型：`string`
  - 含义：原始章回编号文本
  - 示例：`第一回`

- `title`
  - 类型：`string`
  - 含义：章回标题正文，不包含 `第...回`
  - 示例：`甄士隐梦幻识通灵 贾雨村风尘怀闺秀`

- `paragraph_count`
  - 类型：`integer`
  - 含义：该章节切分后得到的段落数量
  - 约束：应大于 `0`

- `source_text_length`
  - 类型：`integer`
  - 含义：章节正文在清理空白并重新拼接后的字符长度
  - 说明：该字段用于规模统计，不作为原始文本 offset 使用

### 6.2 Passage 模型

`passages.jsonl` 中每一行表示一个段落对象。

示例：

```json
{
  "passage_id": "passage_000001",
  "chapter_id": "chapter_001",
  "paragraph_id": "chapter_001_paragraph_001",
  "paragraph_no": 1,
  "text": "列位看官：你道此书从何而来？..."
}
```

字段定义：

- `passage_id`
  - 类型：`string`
  - 含义：全书范围内唯一的段落 ID
  - 约束：格式固定为 `passage_000001` 这类六位补零编号

- `chapter_id`
  - 类型：`string`
  - 含义：该段落所属章节 ID
  - 约束：必须能够在 `chapters.json` 中找到对应章节

- `paragraph_id`
  - 类型：`string`
  - 含义：该段落在章内的定位 ID
  - 约束：格式固定为 `chapter_001_paragraph_001`

- `paragraph_no`
  - 类型：`integer`
  - 含义：该段落在所属章节中的顺序号
  - 约束：每章内从 `1` 开始连续递增

- `text`
  - 类型：`string`
  - 含义：段落正文
  - 约束：不得为空字符串

## 7. ID 设计原则

当前数据构建采用稳定可复现的 ID 规则。

### 7.1 Chapter ID

- 生成方式：`chapter_%03d`
- 示例：`chapter_001`
- 设计意图：便于排序、检索与跨文件引用

### 7.2 Passage ID

- 生成方式：`passage_%06d`
- 示例：`passage_000001`
- 设计意图：保证全书范围内唯一

### 7.3 Paragraph ID

- 生成方式：`chapter_id + "_paragraph_" + %03d`
- 示例：`chapter_001_paragraph_001`
- 设计意图：既保留章内位置，又可直接反查所属 chapter

### 7.4 稳定性约束

只要输入文本内容与切分规则不变，ID 应保持稳定。

以下情况会导致 ID 重排：

- 上游清洗文本发生改动
- 章节标题识别规则发生改动
- 段落切分规则发生改动

## 8. 构建流程

当前构建流程如下：

1. 读取 UTF-8 编码的 `data/input/StoneStory.txt`
2. 逐行扫描文本
3. 对每一行执行标题识别前的空白标准化
4. 识别 `第...回` 标题行
5. 将相邻两个章节标题之间的正文归属到同一 chapter
6. 对单章正文按空行切分 paragraph
7. 生成 chapter 对象与 passage 对象
8. 对构建结果执行校验
9. 写出 `chapters.json`
10. 写出 `passages.jsonl`
11. 写出 `build_report.json`

实现入口：

- `main.py`
- `tools/databuilder/cli.py`

核心构建逻辑：

- `tools/databuilder/builder.py`
- `tools/databuilder/validation.py`

## 9. 切分规则

### 9.1 章回切分规则

当前章节标题识别正则为：

```text
^(第[〇零一二三四五六七八九十百千万两]+回)\s+(.+)$
```

规则说明：

- 行首必须出现 `第...回`
- 编号部分支持常见中文数字
- `回` 后必须有空白
- 空白后的内容全部视为标题正文

处理策略：

- 识别到新标题时，结束上一章
- 第一章标题之前的书名、作者等前置文本不进入输出
- 标题中的连续空白会先被标准化，以兼容半角、全角等不同空白形式

### 9.2 中文章号解析规则

章节编号从 `chapter_label` 中提取，并转换为阿拉伯数字。

支持示例：

- `第一回` -> `1`
- `第十回` -> `10`
- `第二十回` -> `20`
- `第一百二十回` -> `120`

### 9.3 段落切分规则

当前按空行切分段落：

- 连续非空行视为同一段
- 空行触发当前段落结束
- 段内保留换行
- 行首与行尾空白会被清理

处理目标：

- 保持叙事段落稳定
- 保留诗词与对联等多行内容的基本格式
- 让 `passage` 成为适合检索与引用的最小文本单元

## 10. 合理性判断依据

当前方案的合理性建立在以下前提上：

- 输入文本已完成基础清洗
- 章节标题格式总体稳定
- 段落空行格式可用于切分
- 第一版优先追求“稳定可用的基础结构化”，而不是复杂语义切分

该方案适用于：

- 原文检索
- 章节定位
- 章节摘要生成
- 基础知识问答
- 后续人物、事件、关系的弱标注

## 11. 质量校验建议

当前版本已经实现基础数据构建校验，覆盖以下规则：

- 识别出的章节数必须为 `120`
- `chapter_no` 必须从 `1` 到 `120` 连续
- `chapter_id` 不得重复
- `paragraph_count` 必须大于 `0`
- `passage.text` 不得为空
- 每条 `passage.chapter_id` 都必须能关联到合法 chapter
- 每章内 `paragraph_no` 必须连续
- 可疑字符不得被静默丢弃，应记录命中位置

该报告用于记录：

- chapter 总数
- passage 总数
- 错误数
- 警告数
- 异常项明细

## 12. 当前限制

当前实现仍有以下限制：

- 依赖上游清洗文本的空行质量
- 尚未将可疑字符标记回具体 passage
- 尚未接入 `chapters_detected.json` 做交叉校验
- `source_text_length` 不可直接作为原始字符偏移依据
- 尚未支持多版本输入文本的构建管理

## 13. 演进计划

后续建议按以下顺序扩展：

1. 增加数据构建校验模块与 `build_report.json`
2. 为 chapter 增加摘要字段
3. 为 passage 增加检索辅助字段
4. 构建 `characters / relations / events / quotes` 数据层
5. 将结构化结果沉淀为 skill 可直接消费的知识资产

## 14. 使用说明

运行方式：

```bash
python3 main.py
```

显式指定输入与输出目录：

```bash
python3 main.py \
  --input data/input/StoneStory.txt \
  --output-dir data/output
```
