# Skill Assets

`skill/` 目录用于存放 StoneStory 项目运行时要消费的资产。

这里放的是：

- 人物资产
- 知识资产
- Prompt 模板
- 与 skill 运行时直接相关的 Markdown 和结构化文件

可以把当前仓库简化理解为：

- `skill/`
  - 项目运行时资产层
- `tools/`
  - 本地工具实现层
- `plugins/`
  - Codex plugin 与 skill 入口层
- `data/`
  - 输入数据、构建产物、评估结果

当前 `skill/` 下主要包括：

- `characters/`
  - 人物资产目录
- `knowledge/`
  - 知识资产目录
- `prompts/`
  - Prompt 模板目录

维护原则：

- 尽量使用 Markdown 和轻量结构化文件
- 资产内容应尽量可回溯到输入数据或构建结果
- 不在该目录中混入数据处理代码
