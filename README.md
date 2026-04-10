# StoneStory-skill

围绕《红楼梦》构建的开源 skill 项目，当前主实现语言已经切换为 Python。

第一版目标包括：

- 《红楼梦》知识问答
- 角色对话
- 原文检索与章节定位
- 结构化数据构建

当前已完成的数据构建模块：

- 输入：UTF-8 编码的《红楼梦》清洗文本
- 输出：`chapters.json`、`passages.jsonl`、`build_report.json`
- 切分层级：章回、段落
- 技术方案：Python 标准库实现，轻依赖

## 目录

- `AGENTS.md`：项目协作约束与交付规范
- `CURRENT_TASK.md`：当前阶段任务说明
- `skill/`：技能资产目录，存放知识说明、角色配置、Prompt 等 Markdown / 配置文件
- `tools/databuilder/`：离线数据构建工具代码
- `docs/data-builder.md`：模块设计说明
- `data/output/`：默认输出目录

## 运行方式

```bash
python3 main.py
```

也可以显式传参：

```bash
python3 main.py \
  --input data/input/StoneStory.txt \
  --output-dir data/output
```

## 输出说明

`chapters.json` 中每个 chapter 当前包含：

- `chapter_id`
- `chapter_no`
- `chapter_label`
- `title`
- `paragraph_count`
- `source_text_length`

`passages.jsonl` 中每个 passage 当前包含：

- `passage_id`
- `chapter_id`
- `paragraph_id`
- `paragraph_no`
- `text`

`build_report.json` 当前包含：

- `status`
- `summary`
- `issues`

其中 `summary` 会记录 chapter 数、passage 数、错误数、警告数，`issues` 会记录章节连续性、空 passage、可疑字符等校验结果。

后续可以在此基础上继续扩展：

- 章节摘要
- 人物关系索引
- 描述反查原文
- 贾宝玉 / 林黛玉角色配置与对话数据
