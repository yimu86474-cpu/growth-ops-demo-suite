# 第三方平台候选内容抓取报告

- 生成时间：2026-06-17 00:00:00 (demo)
- 模式：synthetic capture，不访问第三方平台，不读取 cookie/token，不保存真实评论原文。
- 候选数量：3
- 选中样本：`demo-ai-workflow`

## 候选评分

| sample_id | platform | title | risk | decision | score | why_collect |
|---|---|---|---|---|---:|---|
| demo-ai-workflow | douyin_demo | 别再收藏AI工具了，先把一个重复工作变成流程 | low | deep_decompose | 4.80 | 主题和木易当前的 AI 流程自动化、内容资产沉淀、项目 demo 可信表达高度相关。 |
| demo-hot-topic | xiaohongshu_demo | 三天涨粉的AI爆款标题 | low | metadata_only | 2.10 | 可作为反例，提醒公开 demo 不承诺无法核验的结果。 |
| demo-private-comment | wechat_demo | 未脱敏私聊问题 | high | reject_sensitive | 1.00 | 用于验证隐私门禁。 |

## 抓取边界

- 真实系统会通过受控浏览器或 OpenCLI 读取公开可见内容。
- 公开 demo 只使用 synthetic metadata 和 synthetic transcript。
- 只保留标题、摘要、选择理由和转写结果，不保存真实昵称、头像、评论原文或私信。
