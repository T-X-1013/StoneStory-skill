# StoneStory Plugin 结构说明

## 1. 文档定位

本文档只说明 `StoneStory-skill` 中 plugin、skill、tools 与人物资产之间的目录关系。

本文档关注：

- 代码和资产分别放在哪里
- `plugins/` 和 `skill/` 的职责区别
- 后续继续开发时应往哪个目录放内容

本文档不负责：

- 具体命令用法
- 具体人物对话流程
- 具体模型回答策略

## 2. 当前分层

StoneStory 当前按四层组织：

1. `plugins/`
   - Codex 插件壳、命令入口、插件内 skill
2. `tools/`
   - 本地 Python 工具实现
3. `skill/`
   - 项目运行时使用的人物资产与知识资产
4. `data/`
   - 输入数据、构建产物、评估结果

可以简化理解为：

- `plugins/` 负责让 Codex 知道“怎么进入 StoneStory 工作流”
- `tools/` 负责真正执行数据构建、检索和评估
- `skill/` 负责存放人物资产本身
- `data/` 负责存放输入与输出文件

## 3. 关键目录

```text
StoneStory-skill/
├── plugins/stonestory/
│   ├── .codex-plugin/
│   ├── commands/
│   ├── prompts/
│   └── skills/
├── tools/
│   ├── databuilder/
│   ├── characterskill/
│   ├── characterchat/
│   └── charactereval/
├── skill/
│   └── characters/
│       ├── jia-baoyu.skill/
│       └── lin-daiyu.skill/
└── data/
    ├── input/
    ├── output/
    └── eval/
```

## 4. 各层职责

### 4.1 `plugins/stonestory/`

这一层是 Codex 集成层。

其中：

- `.codex-plugin/plugin.json`
  - 定义 plugin 身份与元信息
- `commands/`
  - 存放命令入口描述
- `skills/`
  - 存放给 Codex 使用的工作流 skill
- `prompts/`
  - 存放插件内复用的提示模板

### 4.2 `tools/`

这一层是本地执行层。

当前主要包括：

- `databuilder/`
  - 构建 `chapters.json` 与 `passages.jsonl`
- `characterskill/`
  - 生成人物证据、风格候选与人物资产
- `characterchat/`
  - 组装人物对话 `prompt_payload.json`
- `charactereval/`
  - 生成 `evaluation_report.json`

这部分是真正的工程逻辑，不应复制到 plugin 目录里重复维护。

### 4.3 `skill/characters/`

这一层是项目运行时的人物资产层。

例如：

- `skill/characters/jia-baoyu.skill/`
- `skill/characters/lin-daiyu.skill/`

每个人物目录中存放的是：

- `manifest.json`
- `persona.md`
- `style.md`
- `relations.md`
- `boundaries.md`
- 各类 evidence 与 report 文件

### 4.4 `data/`

这一层是输入输出层。

其中：

- `data/input/`
  - 原始输入数据
- `data/output/`
  - 数据构建与对话构造结果
- `data/eval/`
  - 对话评估报告

## 5. 容易混淆的两个目录

最容易混淆的是：

- `plugins/stonestory/skills/`
- `skill/characters/`

它们的区别是：

- `plugins/stonestory/skills/`
  - 给 Codex 用的技能定义与工作流说明
- `skill/characters/`
  - 给 StoneStory 项目本身用的人物数据资产

前者偏“入口规则”，后者偏“人物内容”。

## 6. 后续开发放哪里

后续如果继续开发，建议按下面的规则放置内容：

- 新增人物资产字段或生成人物资产：
  - 放在 `tools/characterskill/` 与 `skill/characters/`
- 新增对话检索、payload 组装、回答前处理：
  - 放在 `tools/characterchat/`
- 新增评估规则或评估报告结构：
  - 放在 `tools/charactereval/`
- 新增 Codex 入口、插件 skill、命令定义：
  - 放在 `plugins/stonestory/`
