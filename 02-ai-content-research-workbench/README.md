# AI 内容需求研究工作台 Demo

## 产品定位

这个 demo 对应真实流程里的“AI 短视频内容中台 / 内容编导工作台”：把项目过程、公开问题、复盘反馈和业务观察先整理成需求样本，再通过样本准入、选题评分、创作 brief、创作前提示词、脚本草稿和发布包，形成可复核的内容生产链路。

它不是“让 AI 随便写几条文案”，而是展示内容生产前面的用户研究和编导判断流程。

## 目标用户

- 需要稳定输出内容的运营负责人。
- 有业务经验但不会系统化选题的个人创作者。
- 想把项目过程变成可传播内容的 AI 增长顾问。

## 真实流程的脱敏映射

```text
项目过程 / 观众问题 / 复盘反馈 / 业务观察
  -> 样本准入
  -> 需求洞察
  -> 选题评分
  -> 创作 brief
  -> 创作前提示词
  -> 脚本草稿和发布包
  -> 候选资产反哺
```

公开 demo 用 synthetic 数据模拟这个链路，不抓取平台、不读取评论原文、不自动发布。

## 快速体验

![AI 内容需求研究工作台模拟截图](../assets/screenshots/content-research-workbench.svg)

在仓库根目录运行：

```powershell
python .\02-ai-content-research-workbench\demo\run_content_research_demo.py
```

输入：

- [research_inputs.jsonl](demo/sample-data/research_inputs.jsonl)
- [workflow_config.json](demo/sample-data/workflow_config.json)

输出：

- [content-research-report.md](demo/sample-report/content-research-report.md)
- [topic-pool.csv](demo/sample-report/topic-pool.csv)
- [creation-brief.md](demo/sample-report/creation-brief.md)
- [publish-package.md](demo/sample-report/publish-package.md)

## 样本准入规则

| 阶段 | 判断内容 | 输出 |
|---|---|---|
| 敏感检查 | 是否包含真实聊天、真实评论原文、私密信息 | 高敏样本拒绝进入脚本 |
| 场景检查 | 是否有明确业务场景和目标人群 | 缺字段只保留为候选 |
| 证据检查 | 是否来自项目过程、观众问题或复盘反馈 | 影响 evidence 分 |
| 可视化检查 | 是否能录屏、画流程或展示报告 | 影响 visual 分 |
| 转化检查 | 是否能承接课程、咨询、信任建设或复盘 | 影响 conversion 分 |

## 选题评分

```text
total_score =
痛感 * 0.30
+ 可信证据 * 0.25
+ 可视化程度 * 0.20
+ 转化价值 * 0.15
+ 易制作程度 * 0.10
```

只有 `total_score >= 4.0` 且 `effort >= 3` 的样本，才进入脚本队列。

## 可复核点

- 输入样本是否真的经历了准入和评分，而不是直接写文案。
- 高敏样本是否被拒绝进入脚本。
- 选题、brief、创作前提示词和发布包是否能一一对应。
- AI 只生成草稿和候选资产，人负责判断、录制、发布和长期沉淀。
