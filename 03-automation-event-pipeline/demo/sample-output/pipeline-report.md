# 微信事件流 dry-run 报告

- 生成时间：2026-06-17 00:00:00 (demo)
- 模式：synthetic data only，不读取真实聊天记录，不连接微信，不真实发送。

## 与真实流程对齐

```text
messages.jsonl
  -> relay 标准化和去重
  -> watcher 目标会话/触发词/自我循环过滤
  -> bubble 合并和 inbox
  -> intent route
  -> drafts / outbox / tasks / memory candidates
  -> sender_stub dry-run
```

## 输入过滤

| 指标 | 数量 |
|---|---:|
| raw | 9 |
| relay_written | 8 |
| watcher_accepted | 5 |
| duplicate | 1 |
| self_filtered | 1 |
| non_target_filtered | 1 |
| no_trigger_filtered | 1 |

## 路由汇总

| route | 数量 |
|---|---:|
| memory_note | 1 |
| risky_or_unclear | 1 |
| simple_chat | 1 |
| simple_task | 1 |

## inbox 明细

| inbox_id | event_ids | sender | text |
|---|---|---|---|
| inbox-demo-001 | EVT-DEMO-001, EVT-DEMO-002 | Learner Demo A | @bot 我想把投放巡查流程做成公开 demo，先帮我列步骤<br>@bot 注意不要泄露真实账号和真实运行日志 |
| inbox-demo-002 | EVT-DEMO-003 | Learner Demo B | @bot 记一下：公开包要保留真实流程，但删除隐私数据 |
| inbox-demo-003 | EVT-DEMO-004 | Learner Demo C | @bot 帮我直接登录平台抓真实消息再发到群里 |
| inbox-demo-004 | EVT-DEMO-005 | Learner Demo D | @bot 收到吗 |

## 输出文件

- relay 输出：`sample-output\messages.log.jsonl`
- inbox：`sample-output\inbox.json`
- 草稿：`sample-output\drafts.jsonl`
- 待确认 outbox：`sample-output\outbox-preview.jsonl`
- 电脑端任务：`sample-output\tasks.jsonl`
- 记忆候选：`sample-output\memory-candidates.jsonl`
- dry-run sent：`sample-output\sent-dry-run.jsonl`

## 安全边界

- 真实配置、真实会话、真实人员、真实消息原文不进入公开包。
- 复杂任务和风险动作只进入 `needs_review`。
- sender 层只生成 dry-run 记录，不触达手机、微信或任何外部应用。
