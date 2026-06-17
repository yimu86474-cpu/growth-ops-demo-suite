# 架构说明：微信事件流 dry-run Demo

## 核心问题

真实业务消息如果“收到就直接执行动作”，会有四类风险：

- 误触发：普通聊天被当成任务。
- 自我循环：bot 自己的消息又触发 bot。
- 无法复盘：不知道哪条消息生成了哪个草稿或任务。
- 安全风险：真实发送、真实登录、真实平台动作被消息直接触发。

这个 demo 用 synthetic 消息展示真实链路如何拆开这些风险。

## 分层架构

| 层级 | 职责 | demo 中的文件 |
|---|---|---|
| relay | 标准化 JSONL、按 `event_id` 去重 | `messages.log.jsonl` |
| watcher | 目标会话、触发词、自我循环过滤 | `pipeline-report.md` 过滤统计 |
| bubble | 合并同一发送者短时间连续消息 | `inbox.json` |
| intent router | 区分聊天、任务、记忆、复杂任务和风险请求 | `drafts.jsonl` |
| processor | 写草稿、outbox、tasks、memory candidates | `outbox-preview.jsonl`、`tasks.jsonl`、`memory-candidates.jsonl` |
| sender stub | dry-run 消费，不真实发送 | `sent-dry-run.jsonl` |

## 输入样例设计

`messages.jsonl` 故意放了几类边界样本：

- 连续两条同一发送者消息：验证 bubble 合并。
- `记一下`：验证进入记忆候选，而不是直接写长期知识。
- “登录平台 / 真实消息 / 发到群”：验证高风险请求进入 `needs_review`。
- bot 自己发的消息：验证自我循环过滤。
- 重复 `event_id`：验证 relay 去重。
- 非目标会话和无触发词消息：验证 watcher 过滤。

## 输出解释

| 输出 | 说明 |
|---|---|
| `messages.log.jsonl` | relay 层标准化后的消息日志 |
| `inbox.json` | watcher 和 bubble 合并后的待处理任务 |
| `drafts.jsonl` | intent router 和处理层生成的草稿 |
| `outbox-preview.jsonl` | 待人工确认的低风险回复队列 |
| `tasks.jsonl` | 复杂或高风险任务队列 |
| `memory-candidates.jsonl` | 记忆沉淀候选池 |
| `sent-dry-run.jsonl` | sender stub 的 dry-run 归档 |

## 风险控制

- 公开 demo 不保存真实聊天原文。
- 不读取真实配置、真实会话、真实人员或真实消息。
- 默认不真实发送。
- 风险动作只进入 `needs_review`。
- 长期沉淀必须经过人工确认，不能由消息直接写入知识库。
