# Character Assets

`skill/characters/` 用于存放人物运行时资产。

当前第一版优先覆盖：

- `jia-baoyu.skill/`
- `lin-daiyu.skill/`

每个人物使用一个独立的 `.skill` 目录，目录中的内容不只是 prompt 片段，而是一组可被程序和 skill 共同消费的人物资产。

当前人物目录中常见文件包括：

- `manifest.json`
  - 程序可读的人物元信息、别名、检索词和排除词
- `README.md`
  - 该人物目录的维护说明
- `persona.md`
  - 数据约束版人物说明
- `style.md`
  - 基于证据候选整理出的风格文档
- `boundaries.md`
  - 回答边界与禁止事项
- `examples.md`
  - 示例或示例生成约束
- `relations.md`
  - 人物关系事实
- `evidence_passages.jsonl`
  - 原始证据候选
- `evidence_ranked.jsonl`
  - 去噪和排序后的证据
- `style_evidence.jsonl`
  - 更适合分析人物表达风格的证据子集
- `style_summary_candidates.json`
  - 结构化风格候选结论
- `source_report.json`
  - 该人物资产构建过程的来源与计数摘要

这些文件共同构成：

- 人物事实层
- 人物证据层
- 人物风格约束层

维护原则：

- 不凭印象直接补写人物设定
- 风格结论尽量回溯到原文证据
- 运行时要消费的内容优先放在该目录，而不是散落在其他位置
