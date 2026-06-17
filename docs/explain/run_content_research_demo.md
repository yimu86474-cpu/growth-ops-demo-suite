---
source_files:
  - 02-ai-content-research-workbench/demo/run_content_research_demo.py
runtime_outputs:
  - 02-ai-content-research-workbench/demo/sample-report/content-research-report.md
  - 02-ai-content-research-workbench/demo/sample-report/topic-pool.csv
  - 02-ai-content-research-workbench/demo/sample-report/creation-brief.md
  - 02-ai-content-research-workbench/demo/sample-report/publish-package.md
verify_commands:
  - python 02-ai-content-research-workbench/demo/run_content_research_demo.py
last_updated: 2026-06-17
---

# run_content_research_demo.py 中文解释

## 它是干什么的

这个脚本模拟“AI 内容需求研究工作台”的真实流程：读取 synthetic 需求样本，进行敏感检查、场景检查、评分排序，然后生成内容研究报告、选题池、创作 brief 和发布包草稿。

## 它读取哪些输入

- `02-ai-content-research-workbench/demo/sample-data/research_inputs.jsonl`
- `02-ai-content-research-workbench/demo/sample-data/workflow_config.json`

可选环境变量：

- `DEMO_GENERATED_AT`：覆盖报告里的生成时间。默认使用固定 demo 时间，避免每次运行都造成 git 工作树变化。

## 它不会读取什么

- 不抓取抖音、小红书、微信或任何平台。
- 不读取 cookie、token、localStorage、Webhook、真实评论原文、私信原文。
- 不自动发布、评论、点赞、收藏、关注。
- 不访问网络。

## 它会产出什么

- `content-research-report.md`：需求研究报告。
- `topic-pool.csv`：选题评分表。
- `creation-brief.md`：最高优先级选题的创作 brief 和创作前提示词。
- `publish-package.md`：短版口播、标题、封面、正文、置顶评论和候选资产。

## 它依赖什么

只依赖 Python 标准库：`csv`、`json`、`os`、`sys`、`dataclasses`、`pathlib`、`typing`。

## 主要判断流程

1. 读取 synthetic 样本。
2. 拒绝高敏样本。
3. 检查业务场景和目标人群。
4. 按痛感、证据、可视化、转化价值和制作难度评分。
5. 达到脚本门禁的样本进入脚本队列。
6. 选择最高分样本生成创作 brief 和发布包草稿。

## 如何验收

运行：

```powershell
python .\02-ai-content-research-workbench\demo\run_content_research_demo.py
```

看到命令输出四个生成文件，并确认 `demo/sample-report/` 下的报告、CSV、brief 和发布包被刷新。

## 关联文件

- 产品说明：`02-ai-content-research-workbench/README.md`
- 用户研究说明：`02-ai-content-research-workbench/docs/user-research-demo.md`
- 安全边界：`docs/security/publication-boundary.md`
- 解释映射：`docs/explain/manifest.json`
