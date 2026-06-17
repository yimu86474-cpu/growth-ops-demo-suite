# 公开展示边界说明

## 结论

这个仓库是 public-safe demo suite，不等于直接公开真实生产仓库。公开仓库只保留脱敏后的产品案例、synthetic 数据、demo 说明和可复用流程，不提交真实业务运行现场。

## 为什么不直接公开真实项目

真实项目包含本机运行配置、平台账号关系、投放规则、运行日志、调试截图、逐字稿和历史过程资产。它们能证明项目真实存在，但不适合直接公开。

更安全的做法是：

1. 从真实项目整理出业务问题和产品闭环。
2. 用 synthetic 数据重建 demo 场景。
3. 用 README、产品案例、截图和演示视频展示能力。
4. 真实仓库保留私有，用公开演示包承接外部查阅。

## 永不公开的内容

- `.env`、`*.local.*`、本机配置文件、API key、token、cookie、Webhook。
- 真实广告账户 ID、真实投手姓名、真实投放消耗和转化明细。
- `runtime/`、`output/`、日志、缓存、数据库、token 缓存。
- 平台签名 URL、带鉴权参数的链接、浏览器 profile。
- 微信聊天原文、私信原文、未脱敏逐字稿。
- 可能暴露客户、同事、群聊、账号、设备信息的截图和视频。

## 允许公开的内容

- 产品定位、目标用户、业务流程、指标体系和验收标准。
- 脱敏后的系统架构、数据流、规则设计和风险控制说明。
- synthetic 数据，例如 `ACC-DEMO-001`、`CR-DEMO-001`、`Operator Demo A`。
- 使用 synthetic 数据生成的巡查报告、需求分析 demo 和用户研究 demo。
- 不包含真实账号或真实平台数据的截图、流程图、演示视频。

## 发布前检查

每次准备发布到 GitHub/Gitee 前，至少检查：

```powershell
git status --short
git ls-files
Select-String -Path .\**\* -Pattern "token|cookie|secret|password|api_key|access_token|refresh_token|SESSDATA|bili_jct|wxid_|chatroom" -CaseSensitive:$false
```

扫描命中不等于一定泄露，但必须逐条确认：是文档里的边界词，还是实际凭证/真实数据。

## 对外表达原则

对外重点讲：

- 识别了什么业务问题。
- 怎么拆目标用户和使用场景。
- 设计了什么最小可用流程。
- 用 vibe coding 如何快速落地 demo。
- 如何通过指标、规则、看板和复盘形成闭环。

不要把重点放在真实账号数量、真实客户数据或平台敏感细节上。
