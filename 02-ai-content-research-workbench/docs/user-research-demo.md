# 用户研究 Demo：AI 内容需求研究工作台

## 研究对象

目标人群：有业务经验、想用 AI 提效，但不懂代码或缺少自动化流程意识的人。

这类用户表面上会问“有什么 AI 工具”“怎么写文案”，实际问题往往是：

1. 我的业务流程里哪一步值得自动化？
2. 我不懂代码，怎么描述需求给 AI？
3. 做出来以后怎么判断它有没有价值？
4. 怎么把项目过程变成可发布、可复盘、可沉淀的内容资产？

## Demo 输入

公开 demo 使用 [research_inputs.jsonl](../demo/sample-data/research_inputs.jsonl) 作为 synthetic 输入，样本类型包括：

| 样本类型 | 作用 | 是否可进入脚本 |
|---|---|---|
| `project_log` | 项目过程证据，例如“真实流程不能只抽象成三条规则” | 可进入 |
| `audience_question` | 观众问题，例如“收藏很多工具但不会落地” | 可进入 |
| `review_comment` | 复盘反馈，例如“这个 demo 不像真实流程” | 可进入 |
| `business_observation` | 业务观察，证据不足时先候选 | 候选 |
| `raw_message` | 未脱敏消息或高敏输入 | 拒绝 |

## 处理流程

```text
research_inputs.jsonl
  -> sensitivity gate
  -> 场景/人群字段检查
  -> pain/evidence/visual/conversion/effort 评分
  -> topic-pool.csv
  -> content-research-report.md
  -> creation-brief.md
  -> publish-package.md
```

## 本轮样例结论

脚本会把 `DEMO-PROJECT-001` 选为最高优先级样本：

```text
别把 AI 项目包装成概念，先把真实流程做成可复核 demo
```

原因：

- 痛点来自项目过程，不是空想选题。
- 有可视化证据：终端运行、Markdown 报告、输入输出文件。
- 能承接当前定位：流程自动化、AI 增长和业务流程拆解。
- 不需要暴露真实账号、真实评论、真实后台截图。

## 产物说明

| 产物 | 说明 |
|---|---|
| `content-research-report.md` | 给人看的需求研究报告 |
| `topic-pool.csv` | 可复核的选题评分表 |
| `creation-brief.md` | 本轮最高优先级选题的创作 brief 和创作前提示词 |
| `publish-package.md` | 短版口播、标题、封面、正文、置顶评论和候选资产 |

## 边界

- 不抓取平台后台。
- 不保存昵称、头像、联系方式、评论原文、私信原文。
- 不自动点赞、收藏、评论、关注或发布。
- 输出只到草稿，人确认后再进入真实录制和发布。
