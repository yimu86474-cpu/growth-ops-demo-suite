---
source_files:
  - 02-third-party-content-remix-pipeline/demo/run_content_chain_demo.py
runtime_outputs:
  - 02-third-party-content-remix-pipeline/demo/sample-output/chain-report.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/capture-candidates-report.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/manual-workbench/01-samples/demo-ai-workflow.source-card.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/manual-workbench/02-transcripts/demo-ai-workflow.clean-transcript.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/manual-workbench/03-decomposition/demo-ai-workflow.director-decomposition.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/manual-workbench/04-quality-review/demo-ai-workflow.decomposition-review.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/manual-workbench/09-reuse-library/demo-ai-workflow.reuse-assets.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/knowledge-base-sync-plan.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/rewrite-brief.md
  - 02-third-party-content-remix-pipeline/demo/sample-output/script-package.md
verify_commands:
  - python 02-third-party-content-remix-pipeline/demo/run_content_chain_demo.py
last_updated: 2026-06-17
---

# run_content_chain_demo.py 中文解释

## 它是干什么的

这个脚本模拟“第三方内容对标改写全链路”：读取 synthetic 第三方平台候选内容，筛选适合深拆的样本，读取 synthetic transcript，生成样本准入卡、清洗逐字稿、七遍编导拆解、质量评分、复用资产、知识库同步计划、改写 brief 和脚本包。

## 它读取哪些输入

- `02-third-party-content-remix-pipeline/demo/sample-data/third_party_samples.jsonl`
- `02-third-party-content-remix-pipeline/demo/sample-data/chain_config.json`
- `02-third-party-content-remix-pipeline/demo/sample-data/transcripts/demo-ai-workflow-transcript.txt`

可选环境变量：

- `DEMO_GENERATED_AT`：覆盖报告里的生成时间。默认使用固定 demo 时间，避免每次运行都造成 git 工作树变化。

## 它不会读取什么

- 不访问抖音、小红书、微信或任何第三方平台。
- 不读取 cookie、token、localStorage、Webhook、真实评论、真实私信、真实视频。
- 不写入真实 Obsidian Vault。
- 不自动发布、评论、点赞、收藏或关注。
- 不访问网络。

## 它会产出什么

- `chain-report.md`：全链路总报告。
- `capture-candidates-report.md`：候选抓取和筛选报告。
- `source-card.md`：样本准入卡。
- `clean-transcript.md`：清洗逐字稿和转写说明。
- `director-decomposition.md`：七遍编导拆解。
- `quality-review.md`：质量评分。
- `reuse-assets.md`：复用资产沉淀。
- `knowledge-base-sync-plan.md`：知识库同步计划，只计划不写入。
- `rewrite-brief.md`：改写创作 brief。
- `script-package.md`：木易原创脚本和发布包。

## 它依赖什么

只依赖 Python 标准库：`json`、`os`、`sys`、`dataclasses`、`pathlib`、`typing`。

## 主要判断流程

1. 读取 synthetic 第三方平台候选样本。
2. 按人群贴合、结构价值、证据价值和改写价值评分。
3. 拒绝高敏样本。
4. 选择低风险且分数达标的样本进入深拆。
5. 读取 synthetic transcript，生成样本准入卡和清洗稿。
6. 输出七遍编导拆解和质量评分。
7. 把结构、钩子、句式、CTA 和反例沉淀成复用资产。
8. 生成知识库同步计划，但不写真实知识库。
9. 基于木易自己的项目证据改写脚本包。

## 如何验收

运行：

```powershell
python .\02-third-party-content-remix-pipeline\demo\run_content_chain_demo.py
```

看到命令输出全链路报告、样本准入卡和改写脚本包路径，并确认 `demo/sample-output/` 下的所有产物被刷新。

## 关联文件

- 产品说明：`02-third-party-content-remix-pipeline/README.md`
- 产品案例：`02-third-party-content-remix-pipeline/docs/full-chain-case.md`
- 安全边界：`docs/security/publication-boundary.md`
- 解释映射：`docs/explain/manifest.json`
