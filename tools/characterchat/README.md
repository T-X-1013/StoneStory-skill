# characterchat 目录说明

`tools/characterchat/` 用于实现人物对话上下文构造链路。

## 目录职责

该目录负责：

- 读取人物资产
- 读取用户问题
- 检索关系、风格证据和事实证据
- 组装 `prompt_payload.json`

## 当前文件分工

- `retriever.py`
  - 检索人物相关关系与证据
- `prompt_builder.py`
  - 组装模型可消费的 payload
- `cli.py`
  - 命令行入口
- `__init__.py`
  - 包级说明

## 对应仓库入口

- `main_character_chat.py`

## 主要输入输出

输入：

- `character_id`
- 用户问题
- `skill/characters/<character-id>.skill/` 下的人物资产

输出：

- `data/output/character_chat/<character-id>_prompt_payload.json`

## 对应文档

- `docs/character-chat-implementation.md`
- `docs/stonestory-skill-chat.md`
- `data/output/README.md`
