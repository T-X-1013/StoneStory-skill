---
name: stonestory-roleplay
description: 用于 StoneStory Codex plugin 中的《红楼梦》角色对话总入口与共享工作流。Use when the user wants StoneStory roleplay but has not yet fixed the character, or when direct skills like `$stonestory:baoyu-chat` and `$stonestory:daiyu-chat` need shared workflow and reply-policy guidance.
---

# StoneStory Roleplay

当任务发生在 StoneStory plugin 的角色对话工作流中，并且需要：

- 在贾宝玉 / 林黛玉之间路由
- 给直接人物 skill 提供共享规则
- 基于本地证据构造角色回答
- 对角色回答做结构化评估

使用这个 skill。

## 首选入口

如果用户已经明确角色，优先改用直接 skill：

- 贾宝玉：`$stonestory:baoyu-chat`
- 林黛玉：`$stonestory:daiyu-chat`

只有在用户尚未明确角色，或需要查看 StoneStory 的共享对话规则时，再停留在这个 skill。

## 核心规则

- 不调用外部模型 API。
- 直接使用当前 Codex 模型生成角色回答。
- 对复杂问题，回答前优先构造 `prompt_payload.json`。
- 回答后如有需要，可生成 `evaluation_report.json`。
- 所有角色结论都应尽量回到本地 evidence。
- 在 StoneStory 人物对话模式下，默认只输出最终角色回答，不输出中间分析、步骤说明、检索过程或工具轨迹说明。
- 只有当用户明确要求“解释过程”“展示证据”“说明你查了什么”时，才允许补充过程性说明。
- 若用户想要“像某个人物.skill 在说话”，应在最终输出里使用固定前缀：
  - `jia-baoyu.skill ❯`
  - `lin-daiyu.skill ❯`

## 何时读取参考文件

- 需要看完整工作流：读取 `references/workflow.md`
- 需要决定角色路由：读取 `references/character-routing.md`
- 需要确认回答边界：读取 `references/reply-policy.md`
