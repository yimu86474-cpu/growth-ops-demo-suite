# Release 说明

## v0.1-public-demo

这个 release 提供可下载的 public-safe demo package，压缩包内容只包含脱敏公开演示材料：

- 根 README 和安全边界说明。
- B站投放巡查系统 synthetic 数据、运行脚本、规则配置、样例报告和通知预览。
- AI 内容需求研究工作台 synthetic 输入、运行脚本、选题评分、创作 brief 和发布包草稿。
- 微信事件流 dry-run synthetic 消息、运行脚本、inbox、outbox、tasks、memory candidates 和 dry-run sent。
- README 使用的模拟截图资源。

`release/README.md` 是仓库内的发布说明，不打进 zip 包，避免解压后出现两个同名 README。

## 不包含

- 真实项目仓库。
- `.env`、token、cookie、key、Webhook。
- 真实广告账户、真实投手姓名、真实投放数据。
- runtime/output/logs/database。
- 真实截图、真实录屏、真实逐字稿。

## 打包命令

在仓库根目录运行：

```powershell
$zip = "release/growth-ops-demo-suite-v0.1-public-demo.zip"
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip }
Compress-Archive `
  -Path README.md, .gitignore, assets, 01-bilibili-ad-inspection-demo, 02-ai-content-research-workbench, 03-automation-event-pipeline, docs `
  -DestinationPath $zip `
  -Force
```

打包后仍需人工检查 zip 内容，确认没有被 `.gitignore` 排除的运行现场或媒体原件混入。
