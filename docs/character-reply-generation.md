# 人物回答生成模块设计

## 1. 文档定位

本文档定义 `StoneStory-skill` 中“人物回答生成层”的下一阶段设计。

本文档关注：

- 当前为什么还需要单独的回答生成层
- 这一层建议如何分模块
- 第一版最小闭环应包含什么

本文档不负责：

- 具体模型厂商选型
- 具体 prompt 文案
- 前端或服务部署方案

## 2. 当前状态

当前仓库已经具备：

- 数据构建
- 人物资产生成
- `prompt_payload.json` 生成
- `evaluation_report.json` 生成

当前还没有：

- `prompt_payload.json -> 角色回答` 这一层的正式代码

因此本文档描述的是“下一阶段要实现什么”，不是“当前已落地实现说明”。

## 3. 为什么需要这一层

当前前四个模块只能做到：

1. 生成上下文
2. 约束人物风格
3. 对回答做评估

但中间真正的“回答生成”目前仍依赖外部交互流程，没有一个独立、稳定、可复用的工程模块。

单独补这一层的作用是：

- 统一回答生成入口
- 统一回答文件格式
- 统一与评估模块的串联方式
- 为后续接不同模型或不同运行方式留出接口层

## 4. 第一版目标

第一版建议只做单轮回答生成，不做复杂多轮对话系统。

第一版应满足：

1. 读取 `prompt_payload.json`
2. 调用一个回答生成入口
3. 产出角色回答文本
4. 可选写出结构化回答文件
5. 可选调用评估模块

## 5. 建议目录结构

建议新增：

```text
tools/charactergen/
  __init__.py
  client.py
  generator.py
  response_writer.py
  cli.py
main_character_reply.py
```

若后续需要支持多种提供方，再扩展：

```text
tools/charactergen/
  providers/
    __init__.py
    openai_client.py
    local_client.py
    mock_client.py
```

## 6. 各模块职责

### 6.1 `client.py`

职责：

- 定义统一模型调用接口
- 隔离不同提供方差异

建议输入：

- `messages`
- 模型名称
- 采样参数

建议输出：

- 原始回答结果

### 6.2 `generator.py`

职责：

- 读取 `prompt_payload.json`
- 提取 `messages`
- 调用模型客户端
- 组织结构化回答结果

### 6.3 `response_writer.py`

职责：

- 统一写回答文件
- 控制输出目录和文件命名

建议输出目录：

- `data/output/character_reply/`

### 6.4 `cli.py`

职责：

- 提供命令行入口
- 接收模型参数
- 控制是否自动评估

### 6.5 `main_character_reply.py`

职责：

- 提供仓库根目录统一运行入口

## 7. 建议输入输出

### 7.1 输入

第一版最小输入：

- `prompt_payload.json`
- 模型或生成器配置

### 7.2 输出

建议输出：

- 纯文本回答
- `response.json`

`response.json` 建议至少包含：

- `character_id`
- `character_name`
- `user_query`
- `assistant_response`
- `cited_passage_ids`
- `model_provider`
- `model_name`
- `generation_config`
- `source_prompt_payload`

## 8. 建议执行链路

第一版建议链路如下：

```text
user query
-> prompt payload
-> character reply
-> response.json
-> evaluation_report.json
```

对应到当前仓库就是：

1. `main_character_chat.py`
2. `main_character_reply.py`
3. `main_character_eval.py`

## 9. 当前暂不做

第一版暂不建议引入：

- 多轮记忆管理
- 长会话状态压缩
- 自动版本对比 UI
- 复杂工具调用链
- 与产品前端直接耦合

## 10. 与现有模块的关系

当前推荐职责边界如下：

- `tools/characterchat/`
  - 负责准备上下文
- `tools/charactergen/`
  - 负责生成人物回答
- `tools/charactereval/`
  - 负责评估人物回答

三层职责应保持分离，不建议合并成一个大脚本。
