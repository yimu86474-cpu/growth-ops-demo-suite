from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "sample-data" / "creative_metrics.csv"
CONFIG = ROOT / "sample-data" / "rule_config.json"
REPORT_OUTPUT = ROOT / "sample-report" / "inspection-report.md"
NOTIFICATION_OUTPUT = ROOT / "sample-report" / "notification-preview.md"
EXPLAIN_DOC = "docs/explain/run_inspection_demo.md"

MISSING = object()


@dataclass(frozen=True)
class Alert:
    severity: str
    alert_type: str
    account_id: str
    account_name: str
    operator: str
    creative_id: str
    creative_name: str
    campaign_id: str
    reason: str
    action: str
    route: str
    auto_action: str


def to_float(value: Any) -> float:
    if value is None:
        return 0.0
    text = str(value).strip()
    return float(text) if text else 0.0


def to_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def nested_get(source: dict[str, Any], path: list[str]) -> Any:
    cursor: Any = source
    for part in path:
        if not isinstance(cursor, dict) or part not in cursor:
            return MISSING
        cursor = cursor[part]
    return cursor


def get_cfg(config: dict[str, Any], account_id: str, dotted_path: str, default: Any = None) -> Any:
    path = dotted_path.split(".")
    account_value = nested_get(config.get("accounts", {}).get(account_id, {}), path)
    if account_value is not MISSING:
        return account_value
    global_value = nested_get(config.get("global", {}), path)
    return default if global_value is MISSING else global_value


def route_for(config: dict[str, Any], operator: str) -> str:
    notification = config.get("notification", {})
    operator_routes = notification.get("operator_webhook_envs", {})
    return operator_routes.get(operator, notification.get("default_webhook_env", "DEMO_DINGTALK_DEFAULT"))


def make_alert(
    row: dict[str, str],
    config: dict[str, Any],
    severity: str,
    alert_type: str,
    reason: str,
    action: str,
    auto_action: str = "manual_review",
) -> Alert:
    operator = row["operator"]
    return Alert(
        severity=severity,
        alert_type=alert_type,
        account_id=row["account_id"],
        account_name=row["account_name"],
        operator=operator,
        creative_id=row.get("creative_id", "-") or "-",
        creative_name=row.get("creative_name", "-") or "-",
        campaign_id=row.get("campaign_id", "-") or "-",
        reason=reason,
        action=action,
        route=route_for(config, operator),
        auto_action=auto_action,
    )


def review_action(row: dict[str, str], base_action: str) -> str:
    if to_bool(row.get("skip_autopause")):
        return f"{base_action.rstrip('。；;')}；该创意处于保护/白名单，只告警不进入自动关停候选。"
    return base_action


def inspect_creative(row: dict[str, str], config: dict[str, Any]) -> list[Alert]:
    account_id = row["account_id"]
    cost = to_float(row["cost"])
    cpa = to_float(row["cpa"])
    conversions = to_float(row["conversions"])
    clicks = to_float(row["clicks"])
    roi = to_float(row["roi"])
    cpm = to_float(row["cpm"])
    comment_click_cost = to_float(row["comment_click_cost"])
    conversion_rate = conversions / clicks * 100 if clicks else 0.0
    skip_autopause = to_bool(row.get("skip_autopause"))

    alerts: list[Alert] = []

    if (
        get_cfg(config, account_id, "over_cost.enabled", False)
        and cost > get_cfg(config, account_id, "over_cost.min_cost", 0)
        and conversions > 0
        and cpa > get_cfg(config, account_id, "over_cost.cpa_threshold", 0)
    ):
        alerts.append(
            make_alert(
                row,
                config,
                "P1",
                "OVER_COST",
                f"超成本：消耗 {cost:.1f}，转化 {conversions:.0f}，CPA {cpa:.1f} 高于阈值 "
                f"{get_cfg(config, account_id, 'over_cost.cpa_threshold')}",
                review_action(row, "人工复核素材、人群和承接链路，必要时调整预算或停创意。"),
            )
        )

    if (
        get_cfg(config, account_id, "idle_spend.zero_conversion.enabled", False)
        and cost > get_cfg(config, account_id, "idle_spend.zero_conversion.min_cost", 0)
        and conversions == 0
    ):
        alerts.append(
            make_alert(
                row,
                config,
                "P0",
                "ZERO_CONVERSION",
                f"零转化空耗：消耗 {cost:.1f}，转化 0。",
                review_action(row, "优先检查素材、定向、人群包和承接页，进入人工处理队列。"),
            )
        )

    if (
        get_cfg(config, account_id, "idle_spend.low_conversion_rate.enabled", False)
        and cost >= get_cfg(config, account_id, "idle_spend.low_conversion_rate.min_cost", 0)
        and conversions > 0
        and conversion_rate < get_cfg(config, account_id, "idle_spend.low_conversion_rate.max_conversion_rate", 0)
    ):
        alerts.append(
            make_alert(
                row,
                config,
                "P2",
                "LOW_CONVERSION_RATE",
                f"低效空耗：转化率 {conversion_rate:.2f}% 低于阈值 "
                f"{get_cfg(config, account_id, 'idle_spend.low_conversion_rate.max_conversion_rate')}%。",
                review_action(row, "进入观察队列，复查点击质量、评论点击成本和转化承接。"),
            )
        )

    if (
        get_cfg(config, account_id, "low_roi.enabled", False)
        and cost >= get_cfg(config, account_id, "low_roi.min_cost", 0)
        and 0 < roi < get_cfg(config, account_id, "low_roi.roi_threshold", 0)
    ):
        alerts.append(
            make_alert(
                row,
                config,
                "P2",
                "LOW_ROI",
                f"ROI 下滑：ROI {roi:.2f} 低于阈值 {get_cfg(config, account_id, 'low_roi.roi_threshold')}。",
                review_action(row, "加入复盘列表，确认订单质量、客单价和素材承接是否变化。"),
            )
        )

    auto_pause_enabled = bool(get_cfg(config, account_id, "auto_pause.enabled", False))
    if not auto_pause_enabled or skip_autopause:
        return alerts

    ap_creative = "auto_pause.creative_over_cost"
    if (
        get_cfg(config, account_id, f"{ap_creative}.enabled", False)
        and cost > get_cfg(config, account_id, f"{ap_creative}.min_cost", 0)
        and conversions > 0
    ):
        high_conv = (
            conversions > get_cfg(config, account_id, f"{ap_creative}.high_conv_min_conversions", 0)
            and cpa > get_cfg(config, account_id, f"{ap_creative}.high_conv_cpa_threshold", 0)
        )
        low_conv = (
            conversions < get_cfg(config, account_id, f"{ap_creative}.low_conv_max_conversions", 0)
            and cpa > get_cfg(config, account_id, f"{ap_creative}.low_conv_cpa_threshold", 0)
        )
        if high_conv or low_conv:
            alerts.append(
                make_alert(
                    row,
                    config,
                    "P0",
                    "AUTO_PAUSED_CREATIVE",
                    f"超成本关停候选：转化 {conversions:.0f}，CPA {cpa:.1f}，命中创意级自动处理规则。",
                    "公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。",
                    "pause_creative_dry_run",
                )
            )

    ap_campaign = "auto_pause.campaign_zero_conversion"
    if (
        get_cfg(config, account_id, f"{ap_campaign}.enabled", False)
        and cost > get_cfg(config, account_id, f"{ap_campaign}.min_cost", 0)
        and conversions == 0
    ):
        alerts.append(
            make_alert(
                row,
                config,
                "P0",
                "AUTO_PAUSED_CAMPAIGN",
                f"空耗关停候选：消耗 {cost:.1f}，转化 0，命中计划/创意空耗保护规则。",
                "公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。",
                "pause_campaign_dry_run",
            )
        )

    ap_advanced = "auto_pause.creative_advanced"
    if (
        get_cfg(config, account_id, f"{ap_advanced}.enabled", False)
        and cost > get_cfg(config, account_id, f"{ap_advanced}.min_cost", 0)
        and conversions == 0
        and cpm > get_cfg(config, account_id, f"{ap_advanced}.max_cpm", 0)
        and comment_click_cost > get_cfg(config, account_id, f"{ap_advanced}.max_comment_click_cost", 0)
    ):
        alerts.append(
            make_alert(
                row,
                config,
                "P0",
                "AUTO_PAUSED_CREATIVE_ADVANCED",
                f"高成本空耗关停候选：CPM {cpm:.1f}，评论点击成本 {comment_click_cost:.1f} 均超阈值。",
                "公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。",
                "pause_creative_dry_run",
            )
        )

    ap_high_cost = "auto_pause.creative_high_cost"
    if (
        get_cfg(config, account_id, f"{ap_high_cost}.enabled", False)
        and cost >= get_cfg(config, account_id, f"{ap_high_cost}.min_cost", 0)
        and conversions > 0
        and cpm > get_cfg(config, account_id, f"{ap_high_cost}.max_cpm", 0)
        and comment_click_cost > get_cfg(config, account_id, f"{ap_high_cost}.max_comment_click_cost", 0)
    ):
        alerts.append(
            make_alert(
                row,
                config,
                "P0",
                "AUTO_PAUSED_CREATIVE_HIGH_COST",
                f"高出单成本关停候选：CPM {cpm:.1f}，评论点击成本 {comment_click_cost:.1f} 均超阈值。",
                "公开 demo 只生成 dry-run 标记；真实系统需按权限和审计记录执行。",
                "pause_creative_dry_run",
            )
        )

    return alerts


def check_balance(account_row: dict[str, str], config: dict[str, Any]) -> Alert | None:
    cash = to_float(account_row["cash"])
    today_cost = to_float(account_row["today_cost"])
    yesterday_cost = to_float(account_row["yesterday_cost"])

    if cash < today_cost or cash < yesterday_cost:
        threshold_text = "今日消耗" if cash < today_cost else "昨日消耗"
        threshold_value = today_cost if cash < today_cost else yesterday_cost
        row = dict(account_row)
        row["creative_id"] = "-"
        row["creative_name"] = "account_balance"
        row["campaign_id"] = "-"
        return make_alert(
            row,
            config,
            "P1",
            "LOW_BALANCE",
            f"余额不足：现金余额 {cash:.1f} 低于{threshold_text} {threshold_value:.1f}。",
            "路由给对应运营人确认充值、预算或投放节奏，避免账户断投。",
        )
    return None


def render_report(alerts: list[Alert], total_rows: int, config: dict[str, Any]) -> str:
    generated_at = os.environ.get("DEMO_GENERATED_AT", "2026-06-17 00:00:00 (demo)")
    severity_counts = {level: 0 for level in ("P0", "P1", "P2")}
    type_counts: dict[str, int] = {}
    for alert in alerts:
        severity_counts[alert.severity] += 1
        type_counts[alert.alert_type] = type_counts.get(alert.alert_type, 0) + 1

    lines = [
        "# 模拟投放巡查报告",
        "",
        f"- 生成时间：{generated_at}",
        f"- 输入创意数：{total_rows}",
        f"- 风险项：P0={severity_counts['P0']}，P1={severity_counts['P1']}，P2={severity_counts['P2']}",
        "- 执行动作：公开 demo 只生成报告和通知预览，不连接平台，不执行真实关停。",
        "",
        "## 与真实流程对齐的部分",
        "",
        "- 巡查粒度：以创意为主，账户余额单独汇总。",
        "- 判断方式：全局规则 + 账户级覆盖配置。",
        "- 处理边界：自动关停规则只产出 dry-run 候选，白名单/保护期只告警不关停。",
        "- 通知方式：按运营人路由，未配置运营人时走默认路由；本 demo 只展示环境变量名。",
        "",
        "## 命中类型汇总",
        "",
    ]

    if type_counts:
        lines.extend(["| 告警类型 | 数量 |", "|---|---:|"])
        for alert_type, count in sorted(type_counts.items()):
            lines.append(f"| {alert_type} | {count} |")
    else:
        lines.append("未发现需要处理的风险项。")

    lines.extend(["", "## 风险明细", ""])
    if alerts:
        lines.extend(
            [
                "| 优先级 | 类型 | 账户 | 创意 | 运营人 | 触发原因 | 动作 |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for item in sorted(alerts, key=lambda x: (x.severity, x.account_id, x.creative_id, x.alert_type)):
            lines.append(
                f"| {item.severity} | {item.alert_type} | {item.account_id} | {item.creative_id} | "
                f"{item.operator} | {item.reason} | {item.action} |"
            )

    lines.extend(
        [
            "",
            "## 规则来源",
            "",
            f"- 规则配置：`{CONFIG.relative_to(ROOT)}`",
            f"- 通知配置：`{config.get('notification', {}).get('mode', 'preview_only')}`",
            "",
            "## 安全说明",
            "",
            "所有账户、创意、运营人、数值和路由均为 synthetic demo data。",
            "公开 demo 不读取真实 token、cookie、Webhook、本机 local config、数据库或运行日志。",
            "",
        ]
    )
    return "\n".join(lines)


def render_notification_preview(alerts: list[Alert], config: dict[str, Any]) -> str:
    generated_at = os.environ.get("DEMO_GENERATED_AT", "2026-06-17 00:00:00 (demo)")
    lines = [
        "# 通知预览",
        "",
        f"- 生成时间：{generated_at}",
        "- 模式：preview-only，不读取真实 webhook，不发送外部消息。",
        "- 路由：按运营人分组；找不到运营人路由时使用默认路由环境变量名。",
        "- 去重：真实流程使用 `operator + message_hash` 做短时间窗口去重；这里仅展示哈希。",
        "",
    ]

    if not alerts:
        lines.append("本次没有需要发送的通知。")
        return "\n".join(lines)

    grouped: dict[str, list[Alert]] = {}
    for alert in alerts:
        grouped.setdefault(alert.operator, []).append(alert)

    dedupe_minutes = config.get("notification", {}).get("dedupe_minutes", 5)
    for operator, operator_alerts in sorted(grouped.items()):
        message_seed = "\n".join(
            f"{item.alert_type}|{item.account_id}|{item.creative_id}|{item.reason}" for item in operator_alerts
        )
        message_hash = hashlib.md5(message_seed.encode("utf-8")).hexdigest()[:12]
        route = operator_alerts[0].route
        lines.extend(
            [
                f"## {operator}",
                "",
                f"- 路由环境变量：`{route}`",
                f"- 去重窗口：{dedupe_minutes} 分钟",
                f"- 消息哈希：`{message_hash}`",
                "",
            ]
        )

        accounts: dict[str, list[Alert]] = {}
        for alert in operator_alerts:
            accounts.setdefault(alert.account_id, []).append(alert)

        for account_id, account_alerts in sorted(accounts.items()):
            account_name = account_alerts[0].account_name
            lines.extend(
                [
                    f"### {account_id} / {account_name}",
                    "",
                    "| 优先级 | 类型 | 创意 | 触发原因 | 动作 |",
                    "|---|---|---|---|---|",
                ]
            )
            for alert in sorted(account_alerts, key=lambda x: (x.severity, x.creative_id, x.alert_type)):
                lines.append(
                    f"| {alert.severity} | {alert.alert_type} | {alert.creative_id} | "
                    f"{alert.reason} | {alert.action} |"
                )
            lines.append("")

        balance_alerts = [item for item in operator_alerts if item.alert_type == "LOW_BALANCE"]
        if balance_alerts:
            lines.extend(["余额提醒会附加到账户通知块中，方便运营人同时处理充值和预算节奏。", ""])

    return "\n".join(lines)


def main() -> None:
    with CONFIG.open("r", encoding="utf-8") as file:
        config: dict[str, Any] = json.load(file)

    with INPUT.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    alerts: list[Alert] = []
    account_rows: dict[str, dict[str, str]] = {}
    for row in rows:
        account_rows.setdefault(row["account_id"], row)
        alerts.extend(inspect_creative(row, config))

    for account_row in account_rows.values():
        balance_alert = check_balance(account_row, config)
        if balance_alert is not None:
            alerts.append(balance_alert)

    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.write_text(render_report(alerts, len(rows), config), encoding="utf-8")
    NOTIFICATION_OUTPUT.write_text(render_notification_preview(alerts, config), encoding="utf-8")

    print(f"已生成巡查报告：{REPORT_OUTPUT}")
    print(f"已生成通知预览：{NOTIFICATION_OUTPUT}")


if __name__ == "__main__":
    main()
