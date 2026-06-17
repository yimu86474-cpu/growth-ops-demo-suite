# 模拟投放巡查报告

- 生成时间：2026-06-17 00:00:00 (demo)
- 输入创意数：8
- 风险项：P0=6，P1=6，P2=6
- 执行动作：公开 demo 只生成报告和通知预览，不连接平台，不执行真实关停。

## 与真实流程对齐的部分

- 巡查粒度：以创意为主，账户余额单独汇总。
- 判断方式：全局规则 + 账户级覆盖配置。
- 处理边界：自动关停规则只产出 dry-run 候选，白名单/保护期只告警不关停。
- 通知方式：按运营人路由，未配置运营人时走默认路由；本 demo 只展示环境变量名。

## 命中类型汇总

| 告警类型 | 数量 |
|---|---:|
| AUTO_PAUSED_CAMPAIGN | 1 |
| AUTO_PAUSED_CREATIVE | 2 |
| AUTO_PAUSED_CREATIVE_ADVANCED | 1 |
| AUTO_PAUSED_CREATIVE_HIGH_COST | 1 |
| LOW_BALANCE | 2 |
| LOW_CONVERSION_RATE | 2 |
| LOW_ROI | 4 |
| OVER_COST | 4 |
| ZERO_CONVERSION | 1 |

## 风险明细

| 优先级 | 类型 | 账户 | 创意 | 运营人 | 触发原因 | 动作 |
|---|---|---|---|---|---|---|
| P0 | AUTO_PAUSED_CAMPAIGN | ACC-DEMO-001 | CR-DEMO-001 | Operator Demo A | 空耗关停候选：消耗 86.0，转化 0，命中计划/创意空耗保护规则。 | 公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。 |
| P0 | AUTO_PAUSED_CREATIVE_ADVANCED | ACC-DEMO-001 | CR-DEMO-001 | Operator Demo A | 高成本空耗关停候选：CPM 36.0，评论点击成本 45.0 均超阈值。 | 公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。 |
| P0 | ZERO_CONVERSION | ACC-DEMO-001 | CR-DEMO-001 | Operator Demo A | 零转化空耗：消耗 86.0，转化 0。 | 优先检查素材、定向、人群包和承接页，进入人工处理队列。 |
| P0 | AUTO_PAUSED_CREATIVE | ACC-DEMO-002 | CR-DEMO-004 | Operator Demo B | 超成本关停候选：转化 1，CPA 220.0，命中创意级自动处理规则。 | 公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。 |
| P0 | AUTO_PAUSED_CREATIVE | ACC-DEMO-003 | CR-DEMO-005 | Operator Demo C | 超成本关停候选：转化 1，CPA 210.0，命中创意级自动处理规则。 | 公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。 |
| P0 | AUTO_PAUSED_CREATIVE_HIGH_COST | ACC-DEMO-003 | CR-DEMO-005 | Operator Demo C | 高出单成本关停候选：CPM 70.0，评论点击成本 75.0 均超阈值。 | 公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。 |
| P1 | LOW_BALANCE | ACC-DEMO-001 | - | Operator Demo A | 余额不足：现金余额 80.0 低于今日消耗 120.0。 | 路由给对应运营人确认充值、预算或投放节奏，避免账户断投。 |
| P1 | OVER_COST | ACC-DEMO-001 | CR-DEMO-002 | Operator Demo A | 超成本：消耗 160.0，转化 1，CPA 160.0 高于阈值 120 | 人工复核素材、人群和承接链路，必要时调整预算或停创意。 |
| P1 | OVER_COST | ACC-DEMO-002 | CR-DEMO-004 | Operator Demo B | 超成本：消耗 220.0，转化 1，CPA 220.0 高于阈值 150 | 人工复核素材、人群和承接链路，必要时调整预算或停创意。 |
| P1 | OVER_COST | ACC-DEMO-003 | CR-DEMO-005 | Operator Demo C | 超成本：消耗 210.0，转化 1，CPA 210.0 高于阈值 120 | 人工复核素材、人群和承接链路，必要时调整预算或停创意。 |
| P1 | OVER_COST | ACC-DEMO-004 | CR-DEMO-006 | Operator Demo C | 超成本：消耗 180.0，转化 1，CPA 190.0 高于阈值 120 | 人工复核素材、人群和承接链路，必要时调整预算或停创意；该创意处于保护/白名单，只告警不进入自动关停候选。 |
| P1 | LOW_BALANCE | ACC-DEMO-006 | - | Operator Demo D | 余额不足：现金余额 60.0 低于今日消耗 70.0。 | 路由给对应运营人确认充值、预算或投放节奏，避免账户断投。 |
| P2 | LOW_ROI | ACC-DEMO-001 | CR-DEMO-002 | Operator Demo A | ROI 下滑：ROI 1.10 低于阈值 1.4。 | 加入复盘列表，确认订单质量、客单价和素材承接是否变化。 |
| P2 | LOW_CONVERSION_RATE | ACC-DEMO-002 | CR-DEMO-003 | Operator Demo B | 低效空耗：转化率 0.33% 低于阈值 0.5%。 | 进入观察队列，复查点击质量、评论点击成本和转化承接。 |
| P2 | LOW_CONVERSION_RATE | ACC-DEMO-002 | CR-DEMO-004 | Operator Demo B | 低效空耗：转化率 0.20% 低于阈值 0.5%。 | 进入观察队列，复查点击质量、评论点击成本和转化承接。 |
| P2 | LOW_ROI | ACC-DEMO-002 | CR-DEMO-004 | Operator Demo B | ROI 下滑：ROI 1.00 低于阈值 1.2。 | 加入复盘列表，确认订单质量、客单价和素材承接是否变化。 |
| P2 | LOW_ROI | ACC-DEMO-003 | CR-DEMO-005 | Operator Demo C | ROI 下滑：ROI 0.80 低于阈值 1.4。 | 加入复盘列表，确认订单质量、客单价和素材承接是否变化。 |
| P2 | LOW_ROI | ACC-DEMO-004 | CR-DEMO-006 | Operator Demo C | ROI 下滑：ROI 0.90 低于阈值 1.4。 | 加入复盘列表，确认订单质量、客单价和素材承接是否变化；该创意处于保护/白名单，只告警不进入自动关停候选。 |

## 规则来源

- 规则配置：`sample-data\rule_config.json`
- 通知配置：`preview_only`

## 安全说明

所有账户、创意、运营人、数值和路由均为 synthetic demo data。
公开 demo 不读取真实 token、cookie、Webhook、本机 local config、数据库或运行日志。
