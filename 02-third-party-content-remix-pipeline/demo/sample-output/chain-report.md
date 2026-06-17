# 第三方内容对标改写全链路报告

- 生成时间：2026-06-17 00:00:00 (demo)
- 候选样本数：3
- 选中样本：`demo-ai-workflow`
- 样本分数：4.80
- 模式：synthetic data only；不访问第三方平台，不写入真实知识库。

## 链路

```text
第三方平台公开内容候选
  -> 候选筛选
  -> synthetic transcript
  -> 样本准入卡
  -> 清洗逐字稿
  -> 七遍编导拆解
  -> 质量评分
  -> 复用资产沉淀
  -> 知识库同步计划
  -> 改写 brief
  -> 木易原创脚本包
```

## 产物

- `sample-output/capture-candidates-report.md`
- `sample-output/manual-workbench/01-samples/demo-ai-workflow.source-card.md`
- `sample-output/manual-workbench/02-transcripts/demo-ai-workflow.clean-transcript.md`
- `sample-output/manual-workbench/03-decomposition/demo-ai-workflow.director-decomposition.md`
- `sample-output/manual-workbench/04-quality-review/demo-ai-workflow.decomposition-review.md`
- `sample-output/manual-workbench/09-reuse-library/demo-ai-workflow.reuse-assets.md`
- `sample-output/knowledge-base-sync-plan.md`
- `sample-output/rewrite-brief.md`
- `sample-output/script-package.md`

## 安全边界

- 不保存真实视频、真实评论、真实账号、真实头像、联系方式或私信。
- 不照搬第三方原句和案例，只迁移结构和方法。
- 不真实写入 Obsidian；公开 demo 只生成同步计划。
- 不自动发布、评论、点赞、收藏或关注。
