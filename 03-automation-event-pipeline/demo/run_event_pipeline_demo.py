from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "sample-data" / "messages.jsonl"
CONFIG = ROOT / "sample-data" / "pipeline_rules.json"
OUT_DIR = ROOT / "sample-output"
MESSAGES_LOG = OUT_DIR / "messages.log.jsonl"
INBOX = OUT_DIR / "inbox.json"
DRAFTS = OUT_DIR / "drafts.jsonl"
OUTBOX = OUT_DIR / "outbox-preview.jsonl"
TASKS = OUT_DIR / "tasks.jsonl"
MEMORY = OUT_DIR / "memory-candidates.jsonl"
SENT = OUT_DIR / "sent-dry-run.jsonl"
REPORT = OUT_DIR / "pipeline-report.md"
EXPLAIN_DOC = "docs/explain/run_event_pipeline_demo.md"


@dataclass(frozen=True)
class Event:
    event_id: str
    source: str
    chat_id: str
    chat_name: str
    sender_id: str
    sender_name: str
    text: str
    created_at: str


@dataclass(frozen=True)
class InboxItem:
    inbox_id: str
    chat_id: str
    chat_name: str
    sender_id: str
    sender_name: str
    text: str
    event_ids: list[str]
    created_at: str


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def as_event(row: dict[str, Any]) -> Event:
    return Event(
        event_id=str(row["event_id"]),
        source=str(row["source"]),
        chat_id=str(row["chat_id"]),
        chat_name=str(row["chat_name"]),
        sender_id=str(row["sender_id"]),
        sender_name=str(row["sender_name"]),
        text=str(row["text"]),
        created_at=str(row["created_at"]),
    )


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def standardize_events(raw_rows: list[dict[str, Any]], config: dict[str, Any]) -> tuple[list[Event], list[Event], dict[str, int]]:
    seen: set[str] = set()
    relay_events: list[Event] = []
    watcher_events: list[Event] = []
    stats = {
        "raw": len(raw_rows),
        "relay_written": 0,
        "watcher_accepted": 0,
        "duplicate": 0,
        "self_filtered": 0,
        "non_target_filtered": 0,
        "no_trigger_filtered": 0,
    }

    target_chats = set(config["target_chats"])
    bot_sender_ids = set(config["bot_sender_ids"])
    mentions = tuple(config["mentions"])

    for row in raw_rows:
        event = as_event(row)
        if event.event_id in seen:
            stats["duplicate"] += 1
            continue
        seen.add(event.event_id)

        relay_events.append(event)

        if event.sender_id in bot_sender_ids:
            stats["self_filtered"] += 1
            continue

        if event.chat_id not in target_chats:
            stats["non_target_filtered"] += 1
            continue

        if not event.text.startswith(mentions):
            stats["no_trigger_filtered"] += 1
            continue

        watcher_events.append(event)

    stats["relay_written"] = len(relay_events)
    stats["watcher_accepted"] = len(watcher_events)
    return relay_events, watcher_events, stats


def merge_bubbles(events: list[Event], config: dict[str, Any]) -> list[InboxItem]:
    if not events:
        return []

    window_seconds = int(config["bubble"]["window_seconds"])
    max_messages = int(config["bubble"]["max_messages"])
    sorted_events = sorted(events, key=lambda item: item.created_at)
    inbox: list[InboxItem] = []
    current: list[Event] = []

    def flush(items: list[Event]) -> None:
        if not items:
            return
        first = items[0]
        text = "\n".join(item.text for item in items)
        inbox.append(
            InboxItem(
                inbox_id=f"inbox-demo-{len(inbox) + 1:03d}",
                chat_id=first.chat_id,
                chat_name=first.chat_name,
                sender_id=first.sender_id,
                sender_name=first.sender_name,
                text=text,
                event_ids=[item.event_id for item in items],
                created_at=first.created_at,
            )
        )

    for event in sorted_events:
        if not current:
            current = [event]
            continue

        previous = current[-1]
        same_thread = event.chat_id == previous.chat_id and event.sender_id == previous.sender_id
        gap = (parse_time(event.created_at) - parse_time(previous.created_at)).total_seconds()
        if same_thread and gap <= window_seconds and len(current) < max_messages:
            current.append(event)
        else:
            flush(current)
            current = [event]

    flush(current)
    return inbox


def route_intent(item: InboxItem, config: dict[str, Any]) -> tuple[str, str, str]:
    text = item.text
    if any(keyword in text for keyword in config["memory_keywords"]):
        return "memory_note", "candidate", "记忆/沉淀触发，进入候选池等待人工确认。"
    if any(keyword in text for keyword in config["risk_keywords"]):
        return "risky_or_unclear", "needs_review", "涉及真实发送、登录、平台动作或隐私风险，进入人工复核任务。"
    if any(keyword in text for keyword in config["complex_keywords"]):
        return "complex_task", "needs_review", "复杂任务进入电脑端任务队列，不由消息直接执行。"
    if any(keyword in text for keyword in config["task_keywords"]):
        return "simple_task", "draft_only", "生成老师型草稿和待确认 outbox。"
    return "simple_chat", "draft_only", "生成简短草稿，不自动真实发送。"


def draft_text(item: InboxItem, route: str) -> str:
    if route == "memory_note":
        return "已整理为候选记忆：公开 demo 要保留真实流程，同时删除隐私数据。等待人工确认后再沉淀。"
    if route == "simple_task":
        return "可以按三步做：先列输入和边界，再跑 synthetic demo，最后输出报告和人工确认点。"
    if route == "complex_task":
        return "这个任务需要拆成电脑端任务队列处理，我不会直接在消息里执行。"
    if route == "risky_or_unclear":
        return "这个请求涉及高风险动作或隐私边界，我先暂停执行，等待人工确认。"
    return "收到，我会先按 dry-run 流程生成草稿。"


def process_inbox(inbox: list[InboxItem], config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    drafts: list[dict[str, Any]] = []
    outbox: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    memory: list[dict[str, Any]] = []
    sent: list[dict[str, Any]] = []

    for item in inbox:
        route, status, reason = route_intent(item, config)
        draft = {
            "draft_id": f"draft-{item.inbox_id}",
            "inbox_id": item.inbox_id,
            "route": route,
            "status": status,
            "reason": reason,
            "text": draft_text(item, route),
        }
        drafts.append(draft)

        if route in {"simple_chat", "simple_task"}:
            job = {
                "job_id": f"out-{item.inbox_id}",
                "target": item.chat_name,
                "text": draft["text"],
                "status": "pending_approval",
                "risk": "low",
                "source_inbox_id": item.inbox_id,
            }
            outbox.append(job)
            sent.append(
                {
                    "job_id": job["job_id"],
                    "mode": "dry_run",
                    "sent": False,
                    "reason": "公开 demo 只模拟 sender_stub 归档，不触达外部应用。",
                }
            )
        elif route == "memory_note":
            memory.append(
                {
                    "candidate_id": f"mem-{item.inbox_id}",
                    "source_inbox_id": item.inbox_id,
                    "status": "needs_review",
                    "summary": draft["text"],
                }
            )
        else:
            tasks.append(
                {
                    "task_id": f"task-{item.inbox_id}",
                    "source_inbox_id": item.inbox_id,
                    "route": route,
                    "status": "needs_review",
                    "reason": reason,
                }
            )

    return {"drafts": drafts, "outbox": outbox, "tasks": tasks, "memory": memory, "sent": sent}


def render_report(stats: dict[str, int], inbox: list[InboxItem], artifacts: dict[str, list[dict[str, Any]]]) -> str:
    generated_at = os.environ.get("DEMO_GENERATED_AT", "2026-06-17 00:00:00 (demo)")
    route_counts: dict[str, int] = {}
    for draft in artifacts["drafts"]:
        route_counts[draft["route"]] = route_counts.get(draft["route"], 0) + 1

    lines = [
        "# 微信事件流 dry-run 报告",
        "",
        f"- 生成时间：{generated_at}",
        "- 模式：synthetic data only，不读取真实聊天记录，不连接微信，不真实发送。",
        "",
        "## 与真实流程对齐",
        "",
        "```text",
        "messages.jsonl",
        "  -> relay 标准化和去重",
        "  -> watcher 目标会话/触发词/自我循环过滤",
        "  -> bubble 合并和 inbox",
        "  -> intent route",
        "  -> drafts / outbox / tasks / memory candidates",
        "  -> sender_stub dry-run",
        "```",
        "",
        "## 输入过滤",
        "",
        "| 指标 | 数量 |",
        "|---|---:|",
    ]
    for key, value in stats.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## 路由汇总", "", "| route | 数量 |", "|---|---:|"])
    for route, count in sorted(route_counts.items()):
        lines.append(f"| {route} | {count} |")

    lines.extend(["", "## inbox 明细", "", "| inbox_id | event_ids | sender | text |", "|---|---|---|---|"])
    for item in inbox:
        text = item.text.replace("\n", "<br>")
        lines.append(f"| {item.inbox_id} | {', '.join(item.event_ids)} | {item.sender_name} | {text} |")

    lines.extend(
        [
            "",
            "## 输出文件",
            "",
            f"- relay 输出：`{MESSAGES_LOG.relative_to(ROOT)}`",
            f"- inbox：`{INBOX.relative_to(ROOT)}`",
            f"- 草稿：`{DRAFTS.relative_to(ROOT)}`",
            f"- 待确认 outbox：`{OUTBOX.relative_to(ROOT)}`",
            f"- 电脑端任务：`{TASKS.relative_to(ROOT)}`",
            f"- 记忆候选：`{MEMORY.relative_to(ROOT)}`",
            f"- dry-run sent：`{SENT.relative_to(ROOT)}`",
            "",
            "## 安全边界",
            "",
            "- 真实配置、真实会话、真实人员、真实消息原文不进入公开包。",
            "- 复杂任务和风险动作只进入 `needs_review`。",
            "- sender 层只生成 dry-run 记录，不触达手机、微信或任何外部应用。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    with CONFIG.open("r", encoding="utf-8") as file:
        config: dict[str, Any] = json.load(file)

    raw_rows = load_jsonl(INPUT)
    relay_events, watcher_events, stats = standardize_events(raw_rows, config)
    inbox = merge_bubbles(watcher_events, config)
    artifacts = process_inbox(inbox, config)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(MESSAGES_LOG, [event.__dict__ for event in relay_events])
    INBOX.write_text(json.dumps([item.__dict__ for item in inbox], ensure_ascii=False, indent=2), encoding="utf-8")
    write_jsonl(DRAFTS, artifacts["drafts"])
    write_jsonl(OUTBOX, artifacts["outbox"])
    write_jsonl(TASKS, artifacts["tasks"])
    write_jsonl(MEMORY, artifacts["memory"])
    write_jsonl(SENT, artifacts["sent"])
    REPORT.write_text(render_report(stats, inbox, artifacts), encoding="utf-8")

    print(f"已生成事件流报告：{REPORT}")
    print(f"已生成 inbox：{INBOX}")
    print(f"已生成 dry-run 输出目录：{OUT_DIR}")


if __name__ == "__main__":
    main()
