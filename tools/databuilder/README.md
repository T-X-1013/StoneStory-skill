# databuilder 目录说明

`tools/databuilder/` 用于实现《红楼梦》基础数据构建链路。

## 目录职责

该目录负责：

- 读取清洗后的全文 txt
- 按章回切分
- 按段落切分
- 生成 `chapters.json`
- 生成 `passages.jsonl`
- 生成 `build_report.json`

## 当前文件分工

- `builder.py`
  - 核心构建逻辑
- `models.py`
  - 构建结果涉及的数据结构
- `validation.py`
  - 构建后的校验逻辑
- `cli.py`
  - 命令行入口
- `__init__.py`
  - 包级说明

## 对应仓库入口

- `main.py`

## 主要输入输出

输入：

- `data/input/StoneStory.txt`
- `data/input/chapters_detected.json`
- `data/input/quality_report.json`
- `data/input/suspicious_char_report.json`

输出：

- `data/output/chapters.json`
- `data/output/passages.jsonl`
- `data/output/build_report.json`

## 对应文档

- `docs/data-builder.md`
