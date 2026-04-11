# 人物对话模块开发路线图

## 1. 文档定位

本文档用于定义 `StoneStory-skill` 人物对话能力的阶段划分、先后顺序与下一步开发重点。

本文档关注：

- 人物对话能力还需要哪些阶段
- 各阶段之间的依赖关系
- 当前下一步应优先做什么

本文档不负责：

- 解释已经落地代码的实现细节
- 代替评估模块专题说明
- 代替人物资产生成说明

相关文档：

- 已落地实现说明：`docs/character-chat-implementation.md`
- 评估模块说明：`docs/character-chat-eval.md`
- 人物回答生成设计：`docs/character-reply-generation.md`

## 2. 当前阶段判断

当前项目已经具备人物对话所需的基础资产和前四个基础模块，但还没有形成“正式可交付的人物回答生成能力”。

当前已经具备：

- `chapters.json`
- `passages.jsonl`
- 人物关系资产
- 人物原文证据
- 去噪后的风格证据
- `style.md` 证据化风格结论
- `prompt_payload.json` 构造能力
- `evaluation_report.json` 生成能力

当前还缺：

- 正式的人物回答生成层
- 多轮对话状态管理
- 更稳定的自动评估与版本对比
- 面向产品化的调用入口

因此当前定位是：

- 已完成人物对话 baseline
- 还未完成正式回答生成闭环

## 3. 总体阶段

人物对话能力建议按五个阶段推进：

1. 人物对话检索编排
2. `style_evidence.jsonl` 质量增强
3. `style.md` 证据化
4. 对话质量评估
5. 人物回答生成

前四个阶段负责把“资产、上下文、评估”打通，第五阶段负责真正把角色回答生成接上。

## 4. 已完成阶段

### 4.1 阶段一：人物对话检索编排

状态：

- 已完成第一版

产物：

- `tools/characterchat/`
- `main_character_chat.py`
- `data/output/character_chat/<character-id>_prompt_payload.json`

作用：

- 读取人物资产
- 根据用户问题检索风格证据与事实证据
- 组装模型可消费的结构化上下文

### 4.2 阶段二：`style_evidence.jsonl` 质量增强

状态：

- 已完成第一版

产物：

- 更严格的 `style_evidence.jsonl`
- 更新后的 `source_report.json`

作用：

- 优先保留目标人物明确发话的段落
- 降低泛指说话人与多说话人混杂段落的权重

### 4.3 阶段三：`style.md` 证据化

状态：

- 已完成第一版

产物：

- `style_summary_candidates.json`
- 基于证据候选生成的 `style.md`

作用：

- 把风格文件从说明性文字提升为可回溯资产
- 让对话阶段读取到更稳定的风格约束

### 4.4 阶段四：对话质量评估

状态：

- 已完成第一版

产物：

- `tools/charactereval/`
- `main_character_eval.py`
- `data/eval/*.json`

作用：

- 为人物回答生成结构化评估报告
- 汇总自动风险信号
- 预填人工 rubric

## 5. 下一阶段

### 5.1 阶段五：人物回答生成

这是当前最优先的下一阶段。

目标：

- 读取 `prompt_payload.json`
- 调用一个回答生成入口
- 输出角色回答文本或结构化回答文件
- 与评估模块串联成完整单轮闭环

建议产物：

- `tools/charactergen/`
- `main_character_reply.py`
- `data/output/character_reply/`

详细设计见：

- `docs/character-reply-generation.md`

## 6. 后续扩展方向

在阶段五之后，再考虑下面这些能力：

1. 多轮状态管理
2. 回答版本对比
3. 更细的自动评估规则
4. 回答样本集与回归基线
5. 更稳定的产品化入口

## 7. 当前建议

如果继续推进人物对话能力，当前最合理的顺序是：

1. 完成人物回答生成层
2. 将回答生成与评估模块接通
3. 建立一组固定问答样本做回归
4. 再考虑多轮对话与服务化入口
