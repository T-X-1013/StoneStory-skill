# 人物对话评估说明

## 1. 文档定位

本文档说明 `StoneStory-skill` 中人物对话评估模块的用途、输入输出、自动检查内容与人工评审方式。

本文档关注：

- 评估模块当前解决什么问题
- 如何运行评估工具
- `evaluation_report.json` 中主要包含什么
- 自动检查与人工判断分别负责什么

本文档不负责：

- 解释人物资产是如何生成的
- 代替人物对话总实现说明
- 给出最终模型优劣结论

相关文档：

- 人物对话实现说明：`docs/character-chat-implementation.md`
- 人物对话路线图：`docs/character-chat-plan.md`

## 2. 模块目标

当前评估模块的目标，不是自动裁判“这个回答一定好或不好”，而是先提供一套稳定、可复用的评估脚手架。

当前模块主要解决：

- 把 `prompt_payload.json` 与回答绑定到统一报告
- 自动收集一组基础风险信号
- 为人工评审预填 rubric
- 为后续版本对比保留统一格式

## 3. 代码位置

当前实现位置：

- `main_character_eval.py`
- `tools/charactereval/models.py`
- `tools/charactereval/evaluator.py`
- `tools/charactereval/cli.py`

默认输出目录：

- `data/eval/`

## 4. 输入与输出

### 4.1 输入

当前评估工具支持以下输入：

- `prompt_payload.json`
- `.txt` 回答文件
- `.json` 回答文件
- 命令行直接传入的回答字符串

若使用 `.json` 回答文件，当前支持读取以下字段：

- `assistant_response`
- `response`
- `answer`
- `content`
- `cited_passage_ids`

### 4.2 输出

当前输出文件为：

- `evaluation_report.json`

默认建议写入：

- `data/eval/`

## 5. 自动检查负责什么

当前第一版不会直接给出“合格/不合格”的最终结论，而是先输出一组自动检查信号。

当前自动检查主要包括：

- 回答是否为空
- 回答长度
- 是否命中用户问题中的 `query_terms`
- 回答中显式引用了哪些 `passage_id`
- 这些引用是否来自当前检索结果
- 是否命中明显现代表达
- 是否出现保守性不确定表达
- 是否出现角色名字

这些信号的作用是：

- 帮助人工快速发现高风险回答
- 为后续自动化评估升级保留基础字段

## 6. 人工评审负责什么

当前评估模块仍然依赖人工完成关键判断。

当前报告会预填一份人工 rubric，包含以下维度：

- `in_character`
- `answers_user_question`
- `grounded_in_evidence`
- `not_modernized`
- `hallucination_risk`

每一项默认包含：

- `question`
- `score`
- `scale`
- `note`

其中 `score` 默认是 `null`，表示需要人工填写。

当前更合理的职责划分是：

- 自动检查负责“发现风险信号”
- 人工评审负责“给出最终判断”

## 7. 人工评审如何使用报告

建议按下面的顺序阅读 `evaluation_report.json`：

1. 先看自动检查信号
   - 判断回答是否为空、是否明显跑题、是否出现现代表达、是否没有证据引用
2. 再看引用的 `passage_id`
   - 判断回答是否真正建立在当前检索证据上
3. 最后填写人工 rubric
   - 判断是否像这个人物
   - 判断是否真正回答了用户问题
   - 判断是否存在胡编风险

如果自动检查已经出现明显高风险信号，人工评审可以优先记录问题，而不是直接给出高分。

## 8. 使用方式

### 8.1 直接传入回答字符串

```bash
python3 main_character_eval.py \
  --payload data/output/character_chat/jia-baoyu_prompt_payload.json \
  --response "妹妹自然是极好的人，我岂敢轻慢。[passage_001716]"
```

### 8.2 使用回答文件

```bash
python3 main_character_eval.py \
  --payload data/output/character_chat/jia-baoyu_prompt_payload.json \
  --response-file response.json \
  --output data/eval
```

### 8.3 显式传入引用段落

若回答里没有直接写出 `passage_id`，也可以显式传入：

```bash
python3 main_character_eval.py \
  --payload data/output/character_chat/jia-baoyu_prompt_payload.json \
  --response "妹妹自然是极好的人。" \
  --cited-passage-id passage_001716
```

## 9. 当前边界

当前评估模块仍有这些限制：

- 不会自动判断“是否真正像这个人物”
- 不会自动判断“是否真的没有胡编”
- 不会自动比较多个回答版本的优劣
- 现代表达识别仍主要依赖固定词表

因此当前定位仍然是：

- 自动风险信号收集器
- 人工评审辅助工具

而不是：

- 全自动角色回答裁判器

## 10. 后续扩展方向

后续可以沿以下方向继续扩展：

1. 建立回答样本集和版本化评估记录
2. 增加更细的自动风险规则
3. 增加回答版本对比能力
4. 在保留人工抽检的前提下，引入模型辅助 judging
