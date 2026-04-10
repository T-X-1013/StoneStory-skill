# 贾宝玉 Skill

该目录定义 `贾宝玉` 的人物 skill 资产。

当前文件分工：

- `manifest.json`：给程序读取的人物标识、别名和检索提示
- `relations.md`：基于 `data/input/triples.csv` 生成的人际关系清单
- `evidence_passages.jsonl`：基于 `data/output/passages.jsonl` 提取的原文证据段落
- `evidence_ranked.jsonl`：对角色相关段落做去噪和相关性打分后的结果
- `style_evidence.jsonl`：更适合做人物说话风格分析的证据子集
- `source_report.json`：当前人物 skill 的数据来源和计数摘要
- `persona.md`：数据约束版人物说明，不写无证据结论
- `style.md`：风格提炼约束说明
- `boundaries.md`：运行时边界和禁止事项
- `examples.md`：示例生成要求说明

维护原则：

- 事实知识优先来自输入数据和结构化输出，不凭印象补写人物设定。
- 若后续补充人物画像或风格结论，必须给出可回溯证据。
