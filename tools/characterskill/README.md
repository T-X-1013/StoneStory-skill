# characterskill 目录说明

`tools/characterskill/` 用于实现人物 Skill 资产生成链路。

## 目录职责

该目录负责：

- 读取人物 `manifest.json`
- 读取 `triples.csv`
- 读取 `passages.jsonl`
- 生成人物关系文件
- 生成人物证据文件
- 提炼风格证据与风格候选

## 当前文件分工

- `builder.py`
  - 核心人物资产构建逻辑
- `models.py`
  - 人物资产构建涉及的数据结构
- `cli.py`
  - 命令行入口
- `__init__.py`
  - 包级说明

## 对应仓库入口

- `main_character_skill.py`

## 主要输入输出

输入：

- `skill/characters/*/*.skill/manifest.json`
- `data/input/triples.csv`
- `data/output/passages.jsonl`

输出：

- `relations.md`
- `evidence_passages.jsonl`
- `evidence_ranked.jsonl`
- `style_evidence.jsonl`
- `style_summary_candidates.json`
- `source_report.json`
- `persona.md`
- `style.md`

## 对应文档

- `docs/character-skill-builder.md`
