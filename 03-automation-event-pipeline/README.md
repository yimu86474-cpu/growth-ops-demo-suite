# 微信事件流 dry-run Demo

## 产品定位

这个 demo 对应真实项目里的 `wechat-codex-pipe`：把微信或模拟消息转成标准事件流，再经过 watcher、bubble 合并、意图路由、草稿生成、任务队列、记忆候选和 sender dry-run。

它不是泛泛的“自动化底座说明”，而是一个可运行的公开脱敏版本，用 synthetic 消息展示真实链路的输入、判断、输出和安全边界。

## 真实流程的脱敏映射

```text
messages.jsonl
  -> relay 标准化和去重
  -> watcher 目标会话/触发词/自我循环过滤
  -> bubble 合并和 inbox
  -> intent route
  -> drafts / outbox / tasks / memory candidates
  -> sender_stub dry-run
```

## 快速体验

在仓库根目录运行：

```powershell
python .\03-automation-event-pipeline\demo\run_event_pipeline_demo.py
```

输入：

- [messages.jsonl](demo/sample-data/messages.jsonl)
- [pipeline_rules.json](demo/sample-data/pipeline_rules.json)

输出：

- [pipeline-report.md](demo/sample-output/pipeline-report.md)
- [messages.log.jsonl](demo/sample-output/messages.log.jsonl)
- [inbox.json](demo/sample-output/inbox.json)
- [drafts.jsonl](demo/sample-output/drafts.jsonl)
- [outbox-preview.jsonl](demo/sample-output/outbox-preview.jsonl)
- [tasks.jsonl](demo/sample-output/tasks.jsonl)
- [memory-candidates.jsonl](demo/sample-output/memory-candidates.jsonl)
- [sent-dry-run.jsonl](demo/sample-output/sent-dry-run.jsonl)

## 路由规则

| route | 触发样例 | 输出 |
|---|---|---|
| `simple_chat` | “收到吗” | 草稿 + 待确认 outbox |
| `simple_task` | “帮我列步骤” | 老师型草稿 + 待确认 outbox |
| `memory_note` | “记一下 / 沉淀 / 整理一下” | `memory-candidates`，等待人工确认 |
| `complex_task` | 长流程、批量、完整项目 | `tasks`，进入电脑端任务队列 |
| `risky_or_unclear` | 登录平台、真实发送、抓真实消息 | `tasks`，状态 `needs_review` |

## 安全流程

- relay 只标准化 synthetic 消息，不读取真实聊天。
- watcher 会过滤重复事件、自我循环、非目标会话和无触发词消息。
- bubble 合并同一发送者短时间连续消息，避免碎片化任务。
- sender 层只生成 dry-run 记录，不触达微信、手机或外部应用。
- 高风险动作不自动执行，只进入 `needs_review`。

## 可复核点

- 是否能看到 raw -> relay -> watcher -> inbox 的数量变化。
- 是否能看到 `记一下` 进入记忆候选，而不是直接沉淀。
- 是否能看到高风险请求进入任务队列。
- 是否能看到 outbox 只是 `pending_approval`，sender 只是 dry-run。
