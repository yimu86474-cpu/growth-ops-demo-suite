# Growth Ops Demo Suite

这是一个面向增长运营、投放巡查和 AI 自动化流程的 public-safe demo suite。它不是生产仓库的直接复制，而是从真实业务流程中整理出的脱敏公开演示包：保留业务问题、产品流程、字段结构、判断逻辑和复核路径，移除真实账号、真实数据、token、cookie、Webhook、日志和运行现场。

## 一句话定位

用 vibe coding 把增长、投放、内容运营和 AI 自动化场景做成可查阅、可运行、可复核的产品 demo，展示业务问题如何被拆成指标、规则、通知、人工确认和复盘闭环。

## Demo 列表

| Demo | 证明能力 | 当前状态 |
|---|---|---|
| [B站投放巡查系统 Demo](01-bilibili-ad-inspection-demo/README.md) | 业务指标拆解、创意级规则引擎、预警策略、运营通知、人工复核边界 | 已有 synthetic 数据和可运行 demo |
| [第三方内容对标改写全链路 Demo](02-third-party-content-remix-pipeline/README.md) | 第三方内容候选、转写、样本准入、编导拆解、资产沉淀、知识库同步计划、原创改写 | 已有 synthetic 数据和可运行 demo |
| [微信事件流 dry-run Demo](03-automation-event-pipeline/README.md) | relay、watcher、bubble 合并、意图路由、任务队列、发送守卫 | 已有 synthetic 消息和可运行 demo |

## 推荐查看顺序

1. 先看主 demo：[B站投放巡查系统 Demo](01-bilibili-ad-inspection-demo/README.md)。
2. 再看产品案例：[docs/product-case.md](01-bilibili-ad-inspection-demo/docs/product-case.md)。
3. 运行投放巡查 demo：`python 01-bilibili-ad-inspection-demo/demo/run_inspection_demo.py`。
4. 运行内容对标改写 demo：`python 02-third-party-content-remix-pipeline/demo/run_content_chain_demo.py`。
5. 运行微信事件流 demo：`python 03-automation-event-pipeline/demo/run_event_pipeline_demo.py`。
6. 查看安全边界：[publication-boundary.md](docs/security/publication-boundary.md)。

## 预览截图

![B站投放巡查系统模拟看板](assets/screenshots/bilibili-inspection-dashboard.svg)

![第三方内容对标改写全链路模拟截图](assets/screenshots/third-party-content-chain.svg)

## 重点可复核内容

- 如何从真实运营问题里抽象目标用户、场景和痛点。
- 如何把创意级指标、账户级配置覆盖和人工保护规则沉淀成可执行判断。
- 如何把通知路由做成按运营人分组，同时在公开 demo 中只展示预览、不触达外部系统。
- 如何把第三方内容拆成候选抓取、转写、样本准入、编导拆解、资产沉淀、知识库同步计划和原创改写。
- 如何把微信消息拆成 relay、watcher、inbox、intent route、outbox/tasks/memory candidates 和 dry-run sent。
- 如何用 synthetic 数据证明系统逻辑，而不是暴露生产数据。
- 如何把 AI / 自动化作为业务流程的一部分，而不是只做单点工具。

## 截图、视频和 Release

当前仓库使用重绘截图和 synthetic 数据样例，避免误放真实后台截图。

| 类型 | 内容 | 状态 |
|---|---|---|
| README 截图 | 模拟数据看板、规则命中、巡查报告 | 已补模拟截图 |
| 演示视频 | 输入 synthetic 数据 -> 执行三个 demo -> 输出巡查报告、内容链路产物、通知和 dry-run 队列 | 待录制 |
| Release demo 包 | 脱敏 demo zip，包含运行脚本、模拟数据、样例报告 | 已发布 |

## 安全声明

本公开演示包不包含真实平台凭证、真实广告账户、真实投放流水、真实聊天记录、真实逐字稿、真实客户数据或平台签名 URL。所有 demo 数据均为 synthetic 数据，仅用于展示产品思路和系统闭环。
