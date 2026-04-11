# 数据构建说明

## 1. 文档定位

本文档说明 `StoneStory-skill` 中《红楼梦》基础数据是如何被构建出来的。

本文档关注：

- 数据构建模块当前负责什么
- 输入文件、输出文件和代码位置
- 章节与段落的切分规则
- ID 设计与校验边界

本文档不负责：

- 解释人物资产如何生成
- 解释人物对话逻辑如何实现
- 解释问答或模型推理链路

相关文档：

- 人物资产生成说明：`docs/character-skill-builder.md`
- 人物对话实现说明：`docs/character-chat-implementation.md`

## 2. 模块目标

数据构建模块的目标，是先为 StoneStory 提供一套稳定、可追踪、便于扩展的基础文本结构。

当前模块主要解决：

- 从清洗后的 txt 中准确切分出 120 回章节
- 在章节内部完成稳定的段落切分
- 生成章节级与段落级结构化文件
- 为后续检索、引用和知识抽取提供统一 ID 体系

当前模块不负责：

- 自动修复可疑字符
- 自动抽取人物、地点、事件、关系
- 构建向量索引或 embedding 数据

## 3. 代码位置

当前实现入口：

- `main.py`
- `tools/databuilder/cli.py`

核心构建逻辑：

- `tools/databuilder/builder.py`
- `tools/databuilder/validation.py`

## 4. 输入与输出

### 4.1 输入

当前主要输入文件：

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

当前主要输出文件：

- `data/output/chapters.json`
- `data/output/passages.jsonl`
- `data/output/build_report.json`

输出要求：

- 文件编码统一为 UTF-8
- `chapters.json` 使用 JSON 数组格式
- `passages.jsonl` 使用 JSON Lines 格式
- `build_report.json` 输出本次构建后的校验报告

## 5. 当前构建流程

当前构建流程如下：

1. 读取 `data/input/StoneStory.txt`
2. 标准化标题识别前的空白
3. 识别 `第...回` 标题行
4. 将相邻两个标题之间的正文归入同一章节
5. 对单章正文按空行切分段落
6. 生成 chapter 对象与 passage 对象
7. 对构建结果执行校验
8. 写出 `chapters.json`
9. 写出 `passages.jsonl`
10. 写出 `build_report.json`

## 6. 切分规则

### 6.1 章回切分

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
- 第一章标题之前的前置文本不进入输出
- 标题中的连续空白会先被标准化

### 6.2 章号解析

章节编号从 `chapter_label` 中提取，并转换为阿拉伯数字。

当前支持示例：

- `第一回` -> `1`
- `第十回` -> `10`
- `第二十回` -> `20`
- `第一百二十回` -> `120`

### 6.3 段落切分

当前按空行切分段落：

- 连续非空行视为同一段
- 空行触发当前段落结束
- 段内保留换行
- 行首与行尾空白会被清理

处理目标：

- 保持叙事段落稳定
- 尽量保留诗词、对联等多行内容的基本格式
- 让 `passage` 成为适合检索与引用的最小文本单元

## 7. 输出数据模型

### 7.1 `chapters.json`

每个 chapter 当前包含：

- `chapter_id`
- `chapter_no`
- `chapter_label`
- `title`
- `paragraph_count`
- `source_text_length`

这些字段的作用分别是：

- `chapter_id`
  - 章节唯一 ID，例如 `chapter_001`
- `chapter_no`
  - 章节阿拉伯数字序号
- `chapter_label`
  - 原始章回编号文本，例如 `第一回`
- `title`
  - 章回标题正文，不含 `第...回`
- `paragraph_count`
  - 该章节切分出的段落数量
- `source_text_length`
  - 章节正文的字符长度统计值

### 7.2 `passages.jsonl`

每条 passage 当前包含：

- `passage_id`
- `chapter_id`
- `paragraph_id`
- `paragraph_no`
- `text`

这些字段的作用分别是：

- `passage_id`
  - 全书范围内唯一的段落 ID
- `chapter_id`
  - 该段落所属章节 ID
- `paragraph_id`
  - 段落在章内的定位 ID
- `paragraph_no`
  - 段落在所属章节中的顺序号
- `text`
  - 段落正文

## 8. ID 设计原则

当前采用稳定可复现的 ID 规则。

### 8.1 Chapter ID

- 生成方式：`chapter_%03d`
- 示例：`chapter_001`

### 8.2 Passage ID

- 生成方式：`passage_%06d`
- 示例：`passage_000001`

### 8.3 Paragraph ID

- 生成方式：`chapter_id + "_paragraph_" + %03d`
- 示例：`chapter_001_paragraph_001`

### 8.4 稳定性约束

只要输入文本与切分规则不变，ID 应保持稳定。

下列变化会导致 ID 重排：

- 上游清洗文本改动
- 章节标题识别规则改动
- 段落切分规则改动

## 9. 数据校验

当前版本已经实现基于 `build_report.json` 的构建校验。

当前覆盖的检查包括：

- 识别出的章节数必须为 `120`
- `chapter_no` 必须从 `1` 到 `120` 连续
- `chapter_id` 不得重复
- `paragraph_count` 必须大于 `0`
- `passage.text` 不得为空
- 每条 `passage.chapter_id` 都必须能关联到合法 chapter
- 每章内 `paragraph_no` 必须连续
- 可疑字符不得被静默丢弃，应记录命中位置

校验器还会读取 `data/input/` 下的参考报告文件，对当前构建结果执行对齐校验：

- `quality_report.json`
- `chapters_detected.json`
- `suspicious_char_report.json`

当前报告会记录：

- chapter 总数
- passage 总数
- 错误数
- 警告数
- 参考报告中的关键统计值
- 异常项明细

## 10. 使用方式

直接运行：

```bash
python3 main.py
```

显式指定输入与输出目录：

```bash
python3 main.py \
  --input data/input/StoneStory.txt \
  --output-dir data/output
```

## 11. 当前限制

当前实现仍有以下限制：

- 依赖上游清洗文本的空行质量
- 可疑字符已下沉到字符级偏移，但尚未映射回原始 txt 的全局坐标
- `source_text_length` 不可直接作为原始字符偏移依据
- 尚未支持多版本输入文本的构建管理

## 12. 后续扩展方向

后续建议按下面顺序扩展：

1. 将字符级告警继续扩展为原始文本全局坐标定位
2. 为 chapter 增加摘要字段
3. 为 passage 增加检索辅助字段
4. 构建 `characters / relations / events / quotes` 数据层
5. 将结构化结果沉淀为 skill 可直接消费的知识资产
