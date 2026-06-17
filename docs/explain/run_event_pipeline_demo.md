---
source_files:
  - 03-automation-event-pipeline/demo/run_event_pipeline_demo.py
runtime_outputs:
  - 03-automation-event-pipeline/demo/sample-output/pipeline-report.md
  - 03-automation-event-pipeline/demo/sample-output/messages.log.jsonl
  - 03-automation-event-pipeline/demo/sample-output/inbox.json
  - 03-automation-event-pipeline/demo/sample-output/drafts.jsonl
  - 03-automation-event-pipeline/demo/sample-output/outbox-preview.jsonl
  - 03-automation-event-pipeline/demo/sample-output/tasks.jsonl
  - 03-automation-event-pipeline/demo/sample-output/memory-candidates.jsonl
  - 03-automation-event-pipeline/demo/sample-output/sent-dry-run.jsonl
verify_commands:
  - python 03-automation-event-pipeline/demo/run_event_pipeline_demo.py
last_updated: 2026-06-17
---

# run_event_pipeline_demo.py 中文解释

## 它是干什么的

这个脚本模拟 `wechat-codex-pipe` 的公开脱敏链路：读取 synthetic 消息事件，生成 relay 消息日志，执行 watcher 过滤和 bubble 合并，再按 intent route 输出草稿、outbox、任务队列、记忆候选和 dry-run sent 记录。

## 它读取哪些输入

- `03-automation-event-pipeline/demo/sample-data/messages.jsonl`
- `03-automation-event-pipeline/demo/sample-data/pipeline_rules.json`

可选环境变量：

- `DEMO_GENERATED_AT`：覆盖报告里的生成时间。默认使用固定 demo 时间，避免每次运行都造成 git 工作树变化。

## 它不会读取什么

- 不读取真实微信数据库、真实消息、真实会话、真实联系人。
- 不读取 `.env`、token、cookie、Webhook、本机 local config。
- 不连接微信、手机、ADB 或外部应用。
- 不执行真实发送。
- 不访问网络。

## 它会产出什么

- `pipeline-report.md`：给人看的事件流报告。
- `messages.log.jsonl`：relay 标准化后的消息日志。
- `inbox.json`：watcher 和 bubble 合并后的 inbox。
- `drafts.jsonl`：意图路由后的草稿。
- `outbox-preview.jsonl`：待人工确认的低风险回复队列。
- `tasks.jsonl`：复杂或高风险任务队列。
- `memory-candidates.jsonl`：记忆沉淀候选池。
- `sent-dry-run.jsonl`：sender stub dry-run 记录。

## 它依赖什么

只依赖 Python 标准库：`json`、`os`、`sys`、`dataclasses`、`datetime`、`pathlib`、`typing`。

## 主要判断流程

1. relay 层按 `event_id` 去重，并写入标准消息日志。
2. watcher 层过滤 bot 自己、非目标会话和无触发词消息。
3. bubble 层合并同一发送者短时间连续消息。
4. intent router 区分 `simple_chat`、`simple_task`、`memory_note`、`complex_task`、`risky_or_unclear`。
5. 低风险消息进入 outbox preview，但状态仍是 `pending_approval`。
6. 记忆触发进入 `memory-candidates`，等待人工确认。
7. 风险请求进入 `tasks`，状态 `needs_review`。
8. sender 层只生成 dry-run 记录，不真实发送。

## 如何验收

运行：

```powershell
python .\03-automation-event-pipeline\demo\run_event_pipeline_demo.py
```

看到命令输出事件流报告、inbox 和 dry-run 输出目录，并确认 `demo/sample-output/` 下的所有文件被刷新。

## 关联文件

- 产品说明：`03-automation-event-pipeline/README.md`
- 架构说明：`03-automation-event-pipeline/docs/architecture.md`
- 安全边界：`docs/security/publication-boundary.md`
- 解释映射：`docs/explain/manifest.json`
