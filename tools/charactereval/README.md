# charactereval 目录说明

`tools/charactereval/` 用于实现人物回答评估链路。

## 目录职责

该目录负责：

- 读取 `prompt_payload.json`
- 读取回答文本或回答文件
- 汇总自动风险信号
- 生成人工 rubric 骨架
- 输出 `evaluation_report.json`

## 当前文件分工

- `models.py`
  - 评估结果涉及的数据结构
- `evaluator.py`
  - 核心评估逻辑
- `cli.py`
  - 命令行入口
- `__init__.py`
  - 包级说明

## 对应仓库入口

- `main_character_eval.py`

## 主要输入输出

输入：

- `data/output/character_chat/<character-id>_prompt_payload.json`
- 回答字符串或回答文件

输出：

- `data/eval/<character-id>_prompt_payload_evaluation.json`

## 对应文档

- `docs/character-chat-eval.md`
