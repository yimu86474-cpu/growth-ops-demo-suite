# 公开演示包复查清单

## 使用方法

这份清单给复查 agent 或发布前自查使用。每个 demo 发布前都要过一遍。

优先级定义：

- P0：安全阻断项，命中就不能发布。
- P1：外部体验关键项，建议发布前补齐。
- P2：加分项，可进入下一轮迭代。

复查结论只给三种：

- `pass`：可以发布。
- `pass_with_notes`：可以发布，但记录后续优化。
- `blocked`：存在 P0 风险或核心 demo 不可验证。

## 1. 仓库结构

- [ ] P1 顶层 README 存在，并说明这是脱敏公开演示包。
- [ ] P1 README 有 demo 索引，能跳转到每个案例或 demo。
- [ ] P1 每个项目有独立说明：业务背景、目标用户、输入、处理、输出、边界。
- [ ] P1 有 `docs/security/publication-boundary.md` 或等价边界说明。
- [ ] P1 有本清单和 SOP，方便后续复用。
- [ ] P2 目录命名清晰，外部读者不用猜哪个文件该先看。

## 2. 安全脱敏

### 凭证与配置

- [ ] P0 未发现 `.env`、API key、token、cookie、secret、password、Webhook。
- [ ] P0 未发现 `config.local.*`、`*.local.json`、真实本机路径、设备 ID、浏览器 profile。
- [ ] P0 未发现 access token、refresh token、session、签名参数或临时鉴权链接。

### 运行现场

- [ ] P0 未提交 `runtime/`、`output/`、缓存、日志、数据库、outbox、inbox、sent。
- [ ] P0 未提交真实运行报告、真实调试日志、真实错误堆栈里带出的账号信息。
- [ ] P1 示例输出来自 synthetic 数据，并在文档中明确说明。

### 真实业务信息

- [ ] P0 未发现真实账号 ID、真实人员姓名、真实客户名、真实群名。
- [ ] P0 未发现手机号、邮箱、微信号、平台 uid、设备序列号。
- [ ] P0 未发现真实投放消耗、订单、转化、聊天、私信、评论原文。
- [ ] P1 业务指标如果需要展示，已经重生成或改为 synthetic 样例。

### 截图、视频与逐字稿

- [ ] P0 截图没有头像、昵称、后台账号、二维码、通知弹窗、浏览器地址栏敏感参数。
- [ ] P0 视频没有录到真实后台、真实聊天、真实文件路径、真实 token。
- [ ] P0 没有未脱敏逐字稿、会议记录、口播原文、评论原文或私信原文。
- [ ] P1 截图和视频使用 demo 数据，或有明确马赛克/重绘处理。

## 3. README 验收

- [ ] P1 30 秒内能看懂公开演示包定位。
- [ ] P1 README 第一屏说明：这是 public-safe demo，不是生产系统公开仓库。
- [ ] P1 有 2-3 个主推 demo，避免把所有文件平铺给读者。
- [ ] P1 每个 demo 都有一句话价值：解决谁的什么问题。
- [ ] P1 每个 demo 都有入口、截图或视频入口。
- [ ] P1 有运行说明，说明依赖、命令、synthetic 数据入口。
- [ ] P1 有边界声明，说明不包含真实账号、真实数据、真实外部平台操作。

## 4. 产品案例验收

- [ ] P1 先讲业务问题，再讲技术实现。
- [ ] P1 讲清目标用户和使用场景。
- [ ] P1 讲清输入、处理、输出的闭环。
- [ ] P1 讲清 AI、人、规则分别负责什么。
- [ ] P1 讲清验收指标或判断标准。
- [ ] P1 demo 里的 synthetic 数据能支撑案例叙事。
- [ ] P2 有失败兜底、人工确认或安全策略说明。

## 5. Demo 验收

- [ ] P1 不需要真实账号、token、cookie 就能体验。
- [ ] P1 默认使用 synthetic 数据。
- [ ] P1 有最小可跑命令或可打开的页面入口。
- [ ] P1 能看到输入样例、处理过程和输出结果。
- [ ] P1 发送、发布、上传、写入外部系统默认关闭。
- [ ] P1 失败时有可理解的提示，不要求读者猜环境。
- [ ] P2 有一键 demo、录屏或在线预览。

## 6. 发布材料验收

- [ ] P1 有截图，展示关键界面、报告或流程结果。
- [ ] P1 有 Release，说明当前版本可看什么、怎么运行、边界是什么。
- [ ] P1 有需求分析 demo，体现业务拆解能力，而不只是代码能力。
- [ ] P1 有运行说明，外部读者能复现最小闭环。
- [ ] P1 有边界声明，明确真实项目保留私有、公开仓库只展示脱敏 demo。

## 7. 发布扫描建议

在仓库根目录执行，逐条人工确认命中结果：

```powershell
git status --short
git ls-files
Select-String -Path .\**\* -Pattern "token|cookie|secret|password|api_key|access_token|refresh_token|session|Webhook|wxid_|chatroom|SESSDATA|bili_jct" -CaseSensitive:$false
Select-String -Path .\**\* -Pattern "runtime|output|config.local|\\.env|\\.local\\.json|sign=|auth=|xsec|timestamp" -CaseSensitive:$false
```

扫描命中不一定等于泄露。判断标准是：命中内容是否只是安全说明里的关键词，还是实际凭证、真实路径、真实账号、真实数据。

## 8. 复查输出模板

复查 agent 最终按这个格式回复：

```text
复查结论：pass / pass_with_notes / blocked

P0 阻断：
- 无 / 列出文件和原因

P1 必补：
- 文件：问题 -> 建议

P2 后续优化：
- 文件：建议

可以对外强调的亮点：
- 亮点 1
- 亮点 2
- 亮点 3
```

## 9. 发布门禁

只要出现下面任一情况，本轮不能发布：

- 出现真实 token、cookie、key、session 或 Webhook。
- 出现真实账号、真实人员、真实客户、真实聊天或真实业务数据。
- demo 必须依赖真实账号才能运行。
- README 没有边界声明。
- 截图或视频暴露真实后台、真实聊天、真实链接或本机敏感路径。
- Release 没写清楚这是脱敏 demo 和 synthetic 数据。

没有 P0 后，可以带着少量 P2 继续发布；P1 如果影响理解，建议先补齐再发布。
