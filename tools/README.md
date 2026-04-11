# tools 目录说明

`tools/` 目录用于存放 StoneStory 的本地工具实现。

这里放的是：

- 数据构建工具
- 人物资产生成工具
- 人物对话上下文构造工具
- 人物回答评估工具

这里不放的是：

- 运行时人物资产
- plugin / skill 入口定义
- 仅用于调用的 shell 包装脚本

可以把当前工程分层理解为：

- `tools/`
  - 本地工具实现层
- `skill/`
  - 运行时资产层
- `plugins/`
  - Codex plugin / skill 入口层
- `scripts/`
  - 本地调试脚本层

## 当前子目录

### `databuilder/`

作用：

- 从 `StoneStory.txt` 构建 `chapters.json`、`passages.jsonl` 和 `build_report.json`

### `characterskill/`

作用：

- 从关系数据和段落数据构建人物资产
- 生成 `relations.md`、`evidence_ranked.jsonl`、`style.md` 等文件

### `characterchat/`

作用：

- 根据人物资产和用户问题构造 `prompt_payload.json`

### `charactereval/`

作用：

- 对人物回答生成 `evaluation_report.json`

## 当前入口

各工具包通常都有自己的 `cli.py`，仓库根目录也提供了对应的统一入口，例如：

- `main.py`
- `main_character_skill.py`
- `main_character_chat.py`
- `main_character_eval.py`

若只是理解总体结构，建议先看：

- `tools/README.md`
- 各子目录下的 `README.md`
- `docs/` 下对应模块说明
