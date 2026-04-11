# StoneStory-skill

围绕《红楼梦》构建的开源 skill 项目。

当前项目重点包括：

- 《红楼梦》基础数据构建
- 人物 skill 资产生成
- 人物对话上下文构造
- 人物回答评估
- Codex skill / plugin 入口整理

当前仓库已经支持通过 Codex skill 发起人物对话，但仓库内部还没有沉淀出独立的“人物回答生成模块”。

## 当前能力

### 1. 基础数据构建

输入：

- `data/input/StoneStory.txt`

输出：

- `data/output/chapters.json`
- `data/output/passages.jsonl`
- `data/output/build_report.json`

当前能力：

- 按章回切分
- 按段落切分
- 生成稳定 ID
- 输出基础校验报告

### 2. 人物 skill 资产生成

输入：

- `data/input/triples.csv`
- `data/output/passages.jsonl`
- `skill/characters/*/*.skill/manifest.json`

输出：

- `relations.md`
- `evidence_passages.jsonl`
- `evidence_ranked.jsonl`
- `style_evidence.jsonl`
- `style_summary_candidates.json`
- `source_report.json`
- `style.md`

当前原则：

- 先抽取可证实关系和原文证据
- 不直接写无证据支撑的人物判断

### 3. 人物对话上下文构造

输入：

- `character_id`
- 用户问题
- 人物 skill 资产目录

输出：

- `data/output/character_chat/<character-id>_prompt_payload.json`

当前能力：

- 检索人物关系、风格证据、事实证据
- 组装模型可消费的结构化上下文

### 4. 人物回答评估

输入：

- `prompt_payload.json`
- 角色回答文本或回答文件

输出：

- `data/eval/*.json`

当前能力：

- 汇总基础风险信号
- 预填人工 rubric

## 使用方式

### 1. 在 Codex 中发起人物对话

当前面向使用者的主入口是 StoneStory skill。

在 Codex 中使用：

```text
/skills
```

然后选择：

- `stonestory:baoyu-chat`
- `stonestory:daiyu-chat`
- `stonestory:stonestory-roleplay`

详细说明见：

- `docs/stonestory-skill-chat.md`

### 2. 本地构造对话上下文

```bash
python3 main_character_chat.py --character-id jia-baoyu --query "你怎么看黛玉？"
```

或使用本地脚本：

```bash
bash scripts/baoyu-chat "你怎么看黛玉？"
```

这些命令主要用于调试、检查 `prompt_payload.json` 和离线验证，不是当前主对话入口。

### 3. 本地执行评估

```bash
python3 main_character_eval.py \
  --payload data/output/character_chat/jia-baoyu_prompt_payload.json \
  --response "妹妹自然是极好的人，我岂敢轻慢。[passage_001716]"
```

## 测试

运行当前回归测试：

```bash
python3 -m unittest discover -s tests -v
```

当前测试覆盖：

- 数据构建与校验
- 可疑字符字符级告警
- 人物关系抽取与证据过滤
- 风格证据去噪与候选生成
- 人物对话 `prompt_payload` 生成
- 人物回答评估报告生成

## 目录

- `AGENTS.md`
  - 项目协作约束与交付规范
- `CURRENT_TASK.md`
  - 当前阶段任务说明
- `data/`
  - 输入数据、构建输出、评估结果
- `skill/`
  - 项目运行时人物资产与知识资产
- `plugins/stonestory/`
  - StoneStory Codex plugin 与 skill 入口
- `tools/databuilder/`
  - 基础数据构建工具
- `tools/characterskill/`
  - 人物资产生成工具
- `tools/characterchat/`
  - 人物对话上下文构造工具
- `tools/charactereval/`
  - 人物回答评估工具
- `scripts/`
  - 本地调试脚本
- `docs/`
  - 项目设计与使用说明

## 文档

- `docs/data-builder.md`
  - 基础数据构建说明
- `docs/character-skill-builder.md`
  - 人物 skill 资产生成说明
- `docs/character-chat-plan.md`
  - 人物对话开发路线图
- `docs/character-chat-implementation.md`
  - 已落地的人物对话实现说明
- `docs/character-chat-eval.md`
  - 人物回答评估模块说明
- `docs/character-reply-generation.md`
  - 人物回答生成模块设计
- `docs/stonestory-plugin-layout.md`
  - plugin / skill / tools / data 结构说明
- `docs/stonestory-skill-chat.md`
  - StoneStory skill 对话说明
- `docs/stonestory-terminal-commands.md`
  - 本地脚本与调试说明

## 当前边界

当前已经具备：

- 数据构建
- 人物资产生成
- 对话上下文构造
- 对话评估
- Codex skill 入口
- 可通过 skill 发起单轮人物对话

当前尚不具备：

- 独立的回答生成代码层
- 稳定多轮状态管理
- 自动化回答优劣裁判
