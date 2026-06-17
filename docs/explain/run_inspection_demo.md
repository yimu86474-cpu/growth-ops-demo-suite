---
source_files:
  - 01-bilibili-ad-inspection-demo/demo/run_inspection_demo.py
runtime_outputs:
  - 01-bilibili-ad-inspection-demo/demo/sample-report/inspection-report.md
  - 01-bilibili-ad-inspection-demo/demo/sample-report/notification-preview.md
verify_commands:
  - python 01-bilibili-ad-inspection-demo/demo/run_inspection_demo.py
last_updated: 2026-06-17
---

# run_inspection_demo.py 中文解释

## 它是干什么的

这个脚本读取脱敏的创意级投放指标和规则配置，模拟一次投放巡查：识别风险创意、账户余额风险和 dry-run 自动处理候选，并生成 Markdown 巡查报告与通知预览。

## 它读取哪些输入

- `01-bilibili-ad-inspection-demo/demo/sample-data/creative_metrics.csv`
- `01-bilibili-ad-inspection-demo/demo/sample-data/rule_config.json`

`creative_metrics.csv` 字段包括 synthetic 账户 ID、账户名、运营人、创意 ID、计划 ID、消耗、CPA、转化、点击、ROI、CPM、评论点击成本、账户现金余额、今日消耗、昨日消耗和 `skip_autopause`。

`rule_config.json` 包括全局规则、账户级覆盖规则和通知路由环境变量名。环境变量名只是占位说明，脚本不会读取真实 webhook 值。

可选环境变量：

- `DEMO_GENERATED_AT`：覆盖报告里的生成时间。默认使用固定 demo 时间，避免每次运行都造成 git 工作树变化。

## 它不会读取什么

- 不读取真实 B站 API。
- 不读取 `.env`、token、cookie、Webhook、local config。
- 不读取真实数据库、真实账户、真实日志。
- 不执行真实暂停、通知或平台操作。
- 不访问网络。

## 它会产出什么

- `01-bilibili-ad-inspection-demo/demo/sample-report/inspection-report.md`
- `01-bilibili-ad-inspection-demo/demo/sample-report/notification-preview.md`

巡查报告包含命中类型汇总、风险明细、规则来源和安全说明。

通知预览模拟真实通知流程的结构：按运营人分组、按账户聚合、展示路由环境变量名和短时间去重哈希；它不发送任何外部消息。

## 它依赖什么

只依赖 Python 标准库：`csv`、`hashlib`、`json`、`os`、`sys`、`dataclasses`、`pathlib`、`typing`。

## 主要判断流程

脚本按以下顺序处理：

1. 读取规则配置和创意级指标。
2. 对每条创意数据应用全局规则，并用账户级配置覆盖阈值。
3. 判断 `OVER_COST`、`ZERO_CONVERSION`、`LOW_CONVERSION_RATE`、`LOW_ROI`。
4. 如果自动处理总开关开启，且该创意未命中 `skip_autopause`，再判断 dry-run 关停候选。
5. 每个账户单独检查余额，生成 `LOW_BALANCE`。
6. 按运营人生成通知预览，并展示去重哈希。

## 常见失败原因

- CSV 或 JSON 文件路径不存在。
- CSV 字段名被改动。
- 数字字段包含无法转成数字的文本。
- JSON 格式不合法。

## 如何验收

运行：

```powershell
python .\01-bilibili-ad-inspection-demo\demo\run_inspection_demo.py
```

看到命令输出“已生成巡查报告”和“已生成通知预览”，并确认两个 Markdown 输出被刷新：

- `demo/sample-report/inspection-report.md`
- `demo/sample-report/notification-preview.md`

再运行解释契约检查：

```powershell
python C:\Users\杨浩楠\.codex\skills\explain-contract\scripts\check_explain_contracts.py --root "<repo-root>"
```

## 关联文件

- 产品说明：`01-bilibili-ad-inspection-demo/README.md`
- 产品案例：`01-bilibili-ad-inspection-demo/docs/product-case.md`
- 安全边界：`docs/security/publication-boundary.md`
- 解释映射：`docs/explain/manifest.json`
