# StoneStory-skill

围绕《红楼梦》构建的开源 skill 项目。

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

当前已完成的人物 skill 第一版生成模块：

- 输入：`triples.csv`、`passages.jsonl`、人物 `manifest.json`
- 输出：`relations.md`、`evidence_passages.jsonl`、`evidence_ranked.jsonl`、`style_evidence.jsonl`、`source_report.json`
- 生成原则：先抽取可证实关系和原文证据，不直接写无证据的人物判断
- 当前包含两层证据处理：角色相关段落去噪、风格证据提炼

## 目录

- `AGENTS.md`：项目协作约束与交付规范
- `CURRENT_TASK.md`：当前阶段任务说明
- `skill/`：技能资产目录，存放知识说明、角色配置、Prompt 等 Markdown / 配置文件
- `tools/databuilder/`：离线数据构建工具代码
- `tools/characterskill/`：人物 skill 第一版生成工具代码
- `docs/data-builder.md`：模块设计说明
- `docs/character-skill-builder.md`：人物 skill 生成设计说明
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

运行人物 skill 第一版生成器：

```bash
python3 main_character_skill.py
```

## 测试方式

运行当前回归测试：

```bash
python3 -m unittest discover -s tests -v
```

当前测试会覆盖：

- `120` 回与 `3028` 段的构建基线
- `build_report.json` 的汇总统计
- 可疑字符字符级告警字段
- `chapters.json` 与 `passages.jsonl` 的落盘一致性
- 人物 skill 生成器的关系抽取与证据过滤规则
- 人物去噪打分与风格证据筛选规则

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
- 贾宝玉/林黛玉角色配置与对话数据