# StoneStory Commands Conventions

本文档只定义 StoneStory plugin 命令层的统一约定。

说明：

- 当前面向使用者的主入口仍然是 `/skills`
- `commands/` 目录中的文件主要用于 plugin 命令定义与后续兼容
- 不应把这些命令文档理解成当前 terminal 中的默认使用方式

StoneStory plugin 命令统一遵守以下约定：

- 角色 id 只使用：
  - `jia-baoyu`
  - `lin-daiyu`
- 命令参数优先使用：
  - `<character-id> <question>`
  - 或 `<answer>`
- 若参数缺失：
  - 先询问用户，再继续流程
- 对话命令必须先生成：
  - `data/output/character_chat/<character-id>_prompt_payload.json`
- 评估命令必须生成：
  - `data/eval/<character-id>_prompt_payload_evaluation.json`
- 所有回答都只使用当前 Codex 模型，不调用外部模型 API
- 若当前环境不支持 plugin command 直接触发，则回退到：
  - `/skills`
  - `stonestory:baoyu-chat`
  - `stonestory:daiyu-chat`
  - `stonestory:stonestory-roleplay`
