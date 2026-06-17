from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "sample-data" / "third_party_samples.jsonl"
CONFIG = ROOT / "sample-data" / "chain_config.json"
OUTPUT = ROOT / "sample-output"
TRANSCRIPTS = ROOT / "sample-data" / "transcripts"
EXPLAIN_DOC = "docs/explain/run_content_chain_demo.md"


@dataclass(frozen=True)
class Candidate:
    sample_id: str
    platform: str
    content_type: str
    synthetic_url: str
    title: str
    creator_alias: str
    visible_summary: str
    why_collect: str
    audience_fit: int
    structure_fit: int
    evidence_fit: int
    rewrite_value: int
    risk_level: str
    transcript_file: str


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def as_candidate(row: dict[str, Any]) -> Candidate:
    return Candidate(
        sample_id=str(row["sample_id"]),
        platform=str(row["platform"]),
        content_type=str(row["content_type"]),
        synthetic_url=str(row["synthetic_url"]),
        title=str(row["title"]),
        creator_alias=str(row["creator_alias"]),
        visible_summary=str(row["visible_summary"]),
        why_collect=str(row["why_collect"]),
        audience_fit=int(row["audience_fit"]),
        structure_fit=int(row["structure_fit"]),
        evidence_fit=int(row["evidence_fit"]),
        rewrite_value=int(row["rewrite_value"]),
        risk_level=str(row["risk_level"]),
        transcript_file=str(row["transcript_file"]),
    )


def score(candidate: Candidate, config: dict[str, Any]) -> float:
    weights = config["candidate_score_weights"]
    return round(
        candidate.audience_fit * weights["audience_fit"]
        + candidate.structure_fit * weights["structure_fit"]
        + candidate.evidence_fit * weights["evidence_fit"]
        + candidate.rewrite_value * weights["rewrite_value"],
        2,
    )


def decision(candidate: Candidate, config: dict[str, Any]) -> str:
    if candidate.risk_level != "low":
        return "reject_sensitive"
    if not candidate.transcript_file:
        return "metadata_only"
    if score(candidate, config) >= config["quality_gates"]["deep_decompose_min_score"]:
        return "deep_decompose"
    return "quick_note"


def select_candidate(candidates: list[Candidate], config: dict[str, Any]) -> Candidate:
    eligible = [item for item in candidates if decision(item, config) == "deep_decompose"]
    if not eligible:
        eligible = [item for item in candidates if decision(item, config) != "reject_sensitive"]
    return sorted(eligible, key=lambda item: score(item, config), reverse=True)[0]


def read_transcript(candidate: Candidate) -> str:
    path = TRANSCRIPTS / candidate.transcript_file
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_capture_report(candidates: list[Candidate], selected: Candidate, config: dict[str, Any]) -> str:
    generated_at = os.environ.get("DEMO_GENERATED_AT", "2026-06-17 00:00:00 (demo)")
    lines = [
        "# 第三方平台候选内容抓取报告",
        "",
        f"- 生成时间：{generated_at}",
        "- 模式：synthetic capture，不访问第三方平台，不读取 cookie/token，不保存真实评论原文。",
        f"- 候选数量：{len(candidates)}",
        f"- 选中样本：`{selected.sample_id}`",
        "",
        "## 候选评分",
        "",
        "| sample_id | platform | title | risk | decision | score | why_collect |",
        "|---|---|---|---|---|---:|---|",
    ]
    for item in sorted(candidates, key=lambda candidate: score(candidate, config), reverse=True):
        lines.append(
            f"| {item.sample_id} | {item.platform} | {item.title} | {item.risk_level} | "
            f"{decision(item, config)} | {score(item, config):.2f} | {item.why_collect} |"
        )
    lines.extend(
        [
            "",
            "## 抓取边界",
            "",
            "- 真实系统会通过受控浏览器或 OpenCLI 读取公开可见内容。",
            "- 公开 demo 只使用 synthetic metadata 和 synthetic transcript。",
            "- 只保留标题、摘要、选择理由和转写结果，不保存真实昵称、头像、评论原文或私信。",
        ]
    )
    return "\n".join(lines)


def render_source_card(candidate: Candidate) -> str:
    return "\n".join(
        [
            "# 样本准入卡",
            "",
            f"sample_id: {candidate.sample_id}",
            f"platform: {candidate.platform}",
            f"content_type: {candidate.content_type}",
            f"source_url: {candidate.synthetic_url}",
            f"source_title: {candidate.title}",
            f"creator_or_account: {candidate.creator_alias}",
            "decision: deep_decompose",
            "",
            "## 我为什么想学它",
            "",
            candidate.why_collect,
            "",
            "## 样本准入检查",
            "",
            f"- 是否服务同一类人群：是，audience_fit={candidate.audience_fit}/5。",
            f"- 是否有明确业务场景：是，主题围绕 AI 工作流落地。",
            f"- 是否有可迁移结构：是，structure_fit={candidate.structure_fit}/5。",
            f"- 是否有真实痛点或冲突：是，强调从工具收藏到流程化。",
            f"- 是否有信任证据：有过程证据，但公开 demo 用 synthetic 描述替代真实截图。",
            f"- 是否能转成我的案例或录屏：能，可替换成自己的 Codex 工作流录屏。",
            f"- 是否主要依赖热点、颜值、人设或平台情绪：否。",
            f"- 是否存在隐私、敏感或搬运风险：风险低；只迁移结构，不搬运原句。",
            "",
            "## 采集摘要",
            "",
            candidate.visible_summary,
            "",
            "## why_worth",
            "",
            "1. 主题与个人 AI 工作台、流程自动化和内容资产沉淀高度相关。",
            "2. 可以迁移成木易自己的项目过程证据，不需要借用原作者结果。",
            "3. 结构适合拆成钩子、痛点、方法、案例和 CTA。",
            "",
            "## why_not",
            "",
            "1. 公开 demo 不使用原视频真实画面和评论，只保留 synthetic 结构。",
            "2. 转写可能缺少画面细节，真实流程里需要人工回看补证据。",
        ]
    )


def render_clean_transcript(candidate: Candidate, transcript: str) -> str:
    return "\n".join(
        [
            "# 清洗逐字稿",
            "",
            f"sample_id: {candidate.sample_id}",
            f"source_url: {candidate.synthetic_url}",
            f"source_title: {candidate.title}",
            "transcript_source: synthetic_transcript_file",
            "transcription_model: demo-small",
            "record_id: DEMO-TRANSCRIPT-001",
            "",
            "## 原始转写说明",
            "",
            "- 公开 demo 使用 synthetic transcript，不来自真实第三方平台。",
            "- 真实流程会记录 record_id、模型、逐字稿路径和术语疑点。",
            "- 本文件用于演示后续编导拆解，不代表真实视频原文。",
            "",
            "## 清洗稿",
            "",
            transcript.strip(),
            "",
            "## 术语疑点",
            "",
            "- 没有真实音频，因此不做语音识别置信度判断。",
            "- 真实流程中 AI/Codex/工作流等术语需要人工校正。",
            "",
            "## 画面线索",
            "",
            "- 可替换画面：终端运行、README diff、报告生成、知识库同步计划。",
            "- 需要避免：真实后台、真实评论、真实账号、未脱敏路径。",
        ]
    )


def evidence_lines(transcript: str) -> list[str]:
    return [line.strip("- ").strip() for line in transcript.splitlines() if line.strip().startswith("-")][:5]


def render_decomposition(candidate: Candidate, transcript: str) -> str:
    evidence = evidence_lines(transcript)
    return "\n".join(
        [
            "# 七遍编导拆解",
            "",
            f"sample_id: {candidate.sample_id}",
            "",
            "## 1. 样本准入",
            "",
            "结论：`deep_decompose`。它不是靠热点，而是靠流程落地痛点，可以迁移到木易自己的 AI 自动化项目。",
            "",
            "## 2. 整体结构",
            "",
            "| 段落 | 功能 | 可迁移方式 |",
            "|---|---|---|",
            "| 开头 | 反转“收藏工具没用” | 改成“只有说明文档没用，流程要跑起来” |",
            "| 痛点 | 用户不会把业务说成流程 | 改成“不会把真实项目脱敏成 demo” |",
            "| 方法 | 输入、判断、输出、验收 | 改成三条可运行 demo 链路 |",
            "| 证据 | 展示工作流产物 | 改成报告、通知预览、知识库同步计划 |",
            "| CTA | 从一个重复动作开始 | 改成先选一个可录屏流程 |",
            "",
            "## 3. 逐句功能",
            "",
            "| 证据片段 | 功能判断 |",
            "|---|---|",
            *[f"| {line} | 支撑用户痛点或方法步骤 |" for line in evidence],
            "",
            "## 4. 用户心理路径",
            "",
            "焦虑：工具很多但不会落地 -> 反思：不是缺工具，是缺流程描述 -> 确定性：按输入/判断/输出拆 -> 行动：拿一个重复工作做 demo。",
            "",
            "## 5. 表达技巧",
            "",
            "- 用反例开头，先打掉“收藏工具/堆文档”的假努力。",
            "- 用三段式流程降低理解成本。",
            "- 用可录屏证据增强可信度。",
            "",
            "## 6. 转化设计",
            "",
            "转化不是硬推服务，而是引导用户把一个重复业务动作交给 AI 拆流程，适合承接课程、咨询或流程自动化服务。",
            "",
            "## 7. 可复用模板",
            "",
            "```text",
            "你不是缺【工具/文档/灵感】，你缺的是把【业务动作】拆成【输入、判断、输出、验收】。",
            "先别急着【生成成品】，先拿一个【重复动作】跑出一个可复核 demo。",
            "```",
        ]
    )


def render_quality_review(candidate: Candidate, config: dict[str, Any]) -> str:
    total = score(candidate, config)
    return "\n".join(
        [
            "# 拆解质量评分",
            "",
            f"sample_id: {candidate.sample_id}",
            f"total_score: {total:.2f}",
            "",
            "| 项目 | score | reason | evidence | uncertainty | next_action |",
            "|---|---:|---|---|---|---|",
            "| 人群贴合 | 5 | 服务想用 AI 落地的业务人群 | 标题和摘要都围绕流程化 | 没有真实评论反馈 | 用自己的评论/问题替换 |",
            "| 结构可迁移 | 5 | 反例开头 + 方法步骤 + CTA 清晰 | 可迁移成工作流 demo | 缺画面节奏 | 录制终端和报告画面 |",
            "| 证据可信 | 4 | 可用项目过程替代原作者案例 | 有可运行脚本和输出 | 公开 demo 是 synthetic | 标注 synthetic 边界 |",
            "| 转化自然 | 4 | CTA 能承接流程咨询/课程 | 从重复动作开始 | 不应承诺收益 | CTA 保持低门槛 |",
            "",
            "结论：通过公开 demo 的深拆门禁，可以进入复用资产沉淀和改写创作。",
        ]
    )


def render_reuse_assets(candidate: Candidate) -> str:
    return "\n".join(
        [
            "# 复用资产沉淀",
            "",
            f"source_sample: {candidate.sample_id}",
            "",
            "## 结构资产",
            "",
            "- asset_type: script_structure",
            "- template: 反例开头 -> 痛点澄清 -> 三步流程 -> 可视化证据 -> 低门槛 CTA",
            "- usable_for: AI 自动化、流程改造、项目 demo、内容生产工作台",
            "",
            "## 钩子资产",
            "",
            "- 你不是缺 AI 工具，你缺的是把业务说成流程。",
            "- AI 项目不是文档堆砌，真正有价值的是流程能跑。",
            "",
            "## 句式资产",
            "",
            "- 先别急着让 AI 生成成品，先把输入、判断、输出写清楚。",
            "- 公开 demo 可以没有真实账号，但不能没有真实流程。",
            "",
            "## CTA 资产",
            "",
            "- 先拿一个你重复做三次的工作，拆成输入、判断、输出。",
            "- 如果你不知道从哪步开始，就先把最近一次手工流程截图列出来。",
            "",
            "## 反例资产",
            "",
            "- 只搬运对标视频原句。",
            "- 只写选题，不保留证据、边界和验收。",
            "- 只展示 Markdown，不展示可运行输入输出。",
        ]
    )


def render_kb_sync_plan(candidate: Candidate) -> str:
    return "\n".join(
        [
            "# 知识库同步计划",
            "",
            "公开 demo 只生成同步计划，不写入真实 Obsidian Vault。",
            "",
            f"- source_sample: `{candidate.sample_id}`",
            "- sync_mode: plan_only",
            "- target_assets:",
            "  - `40-资产库/方法库/内容创作/第三方内容对标拆解流程.md`",
            "  - `40-资产库/素材库/脚本结构/反例开头到流程证据.md`",
            "  - `50-AI记忆/项目调用索引/内容对标改写链路.md`",
            "- required_checks:",
            "  - 不写入真实视频原文。",
            "  - 不写入真实评论、昵称、头像或联系方式。",
            "  - 只保存结构、方法、边界和可替换模板。",
            "  - 真实写入前先走 Obsidian 写入路由和 unresolved 校验。",
        ]
    )


def render_rewrite_brief(candidate: Candidate) -> str:
    return "\n".join(
        [
            "# 改写创作 Brief",
            "",
            f"source_sample: {candidate.sample_id}",
            "- rewrite_goal: 把第三方内容结构迁移成木易自己的 AI 自动化项目脚本。",
            "- target_audience: 有业务经验但不懂代码、想用 AI 落地流程的人。",
            "- own_evidence:",
            "  - 投放巡查 demo 的创意级规则和通知预览。",
            "  - 微信事件流 demo 的 inbox、route、outbox 和 dry-run sent。",
            "  - 内容对标链路 demo 的拆解、资产沉淀和改写包。",
            "- forbidden:",
            "  - 不复刻原作者人设。",
            "  - 不搬运原句。",
            "  - 不承诺无法证明的收益。",
            "  - 不暴露真实平台、真实视频、真实评论或真实知识库路径。",
            "",
            "## 创作前提示词",
            "",
            "请围绕【第三方内容如何变成自己的可复用资产】写一条木易口吻的口播。",
            "目标人群是【有业务经验但不会把 AI 落地到流程的人】。",
            "采用【反例开头 -> 真实流程 -> 项目证据 -> 安全边界 -> 低门槛 CTA】结构。",
            "必须使用木易自己的项目证据，不搬运原作者案例和原句。",
            "输出短版口播、标准版骨架、发布包、质检和候选资产。",
        ]
    )


def render_script_package(candidate: Candidate) -> str:
    return "\n".join(
        [
            "# 改写脚本包",
            "",
            "## 短版口播",
            "",
            "很多人刷到一个好视频，第一反应是让 AI 仿写一条。",
            "但这样做出来的内容，很容易像搬运，也沉淀不出自己的能力。",
            "我的流程不是直接改写，而是先把第三方内容抓成候选样本，再做转写、样本准入、七遍编导拆解。",
            "真正有价值的不是那条原视频，而是它背后的结构：它怎么开头，怎么制造冲突，怎么给证据，怎么转化。",
            "拆完以后，我只把结构、句式方法和 CTA 边界沉淀到知识库，再替换成我自己的项目证据。",
            "比如投放巡查、微信事件流、内容链路这些 demo，都是我自己的流程画面和输出报告。",
            "所以你不要问 AI 能不能仿写，先问：这条内容有什么结构值得学？我有什么自己的证据能替换它？",
            "",
            "## 标准版骨架",
            "",
            "1. 反例：直接仿写第三方视频很危险。",
            "2. 流程：抓取候选 -> 转写 -> 准入 -> 七遍拆解 -> 资产沉淀 -> 改写。",
            "3. 证据：展示 synthetic demo 的 source-card、transcript、decomposition、kb sync plan。",
            "4. 边界：不保存真实评论原文，不照搬原句，不承诺原作者结果。",
            "5. CTA：拿一条你收藏的视频，先拆结构，再替换成自己的项目证据。",
            "",
            "## 发布包",
            "",
            "- 主标题：别再让 AI 仿写视频了，先把它拆成你的内容资产",
            "- 备选标题：第三方内容怎么变成自己的原创脚本？",
            "- 封面文案：别仿写，先拆解",
            "- 正文：一条好内容最值得学的不是原句，而是结构。公开 demo 里我用 synthetic 样本跑完了抓取、转写、拆解、沉淀和改写全链路。",
            "- 置顶评论：你可以先拿一条收藏视频试试：只拆结构，不搬原句，然后换成自己的项目证据。",
            "- CTA：需要的话，我可以继续把这个流程整理成可复用 SOP。",
            "",
            "## 质检",
            "",
            "- 是否搬运原句：否。",
            "- 是否使用自己的证据：是，使用公开 demo 三条流程。",
            "- 是否说明边界：是。",
            "- 是否可录屏：是，可录制 sample-output 文件和报告。",
            "- 是否夸大结果：否。",
        ]
    )


def render_chain_report(candidate: Candidate, candidates: list[Candidate], config: dict[str, Any]) -> str:
    generated_at = os.environ.get("DEMO_GENERATED_AT", "2026-06-17 00:00:00 (demo)")
    return "\n".join(
        [
            "# 第三方内容对标改写全链路报告",
            "",
            f"- 生成时间：{generated_at}",
            f"- 候选样本数：{len(candidates)}",
            f"- 选中样本：`{candidate.sample_id}`",
            f"- 样本分数：{score(candidate, config):.2f}",
            "- 模式：synthetic data only；不访问第三方平台，不写入真实知识库。",
            "",
            "## 链路",
            "",
            "```text",
            "第三方平台公开内容候选",
            "  -> 候选筛选",
            "  -> synthetic transcript",
            "  -> 样本准入卡",
            "  -> 清洗逐字稿",
            "  -> 七遍编导拆解",
            "  -> 质量评分",
            "  -> 复用资产沉淀",
            "  -> 知识库同步计划",
            "  -> 改写 brief",
            "  -> 木易原创脚本包",
            "```",
            "",
            "## 产物",
            "",
            "- `sample-output/capture-candidates-report.md`",
            "- `sample-output/manual-workbench/01-samples/demo-ai-workflow.source-card.md`",
            "- `sample-output/manual-workbench/02-transcripts/demo-ai-workflow.clean-transcript.md`",
            "- `sample-output/manual-workbench/03-decomposition/demo-ai-workflow.director-decomposition.md`",
            "- `sample-output/manual-workbench/04-quality-review/demo-ai-workflow.decomposition-review.md`",
            "- `sample-output/manual-workbench/09-reuse-library/demo-ai-workflow.reuse-assets.md`",
            "- `sample-output/knowledge-base-sync-plan.md`",
            "- `sample-output/rewrite-brief.md`",
            "- `sample-output/script-package.md`",
            "",
            "## 安全边界",
            "",
            "- 不保存真实视频、真实评论、真实账号、真实头像、联系方式或私信。",
            "- 不照搬第三方原句和案例，只迁移结构和方法。",
            "- 不真实写入 Obsidian；公开 demo 只生成同步计划。",
            "- 不自动发布、评论、点赞、收藏或关注。",
        ]
    )


def main() -> None:
    with CONFIG.open("r", encoding="utf-8") as file:
        config: dict[str, Any] = json.load(file)

    candidates = [as_candidate(row) for row in load_jsonl(INPUT)]
    selected = select_candidate(candidates, config)
    transcript = read_transcript(selected)

    write_text(OUTPUT / "capture-candidates-report.md", render_capture_report(candidates, selected, config))
    write_text(OUTPUT / "manual-workbench" / "01-samples" / f"{selected.sample_id}.source-card.md", render_source_card(selected))
    write_text(OUTPUT / "manual-workbench" / "02-transcripts" / f"{selected.sample_id}.clean-transcript.md", render_clean_transcript(selected, transcript))
    write_text(OUTPUT / "manual-workbench" / "03-decomposition" / f"{selected.sample_id}.director-decomposition.md", render_decomposition(selected, transcript))
    write_text(OUTPUT / "manual-workbench" / "04-quality-review" / f"{selected.sample_id}.decomposition-review.md", render_quality_review(selected, config))
    write_text(OUTPUT / "manual-workbench" / "09-reuse-library" / f"{selected.sample_id}.reuse-assets.md", render_reuse_assets(selected))
    write_text(OUTPUT / "knowledge-base-sync-plan.md", render_kb_sync_plan(selected))
    write_text(OUTPUT / "rewrite-brief.md", render_rewrite_brief(selected))
    write_text(OUTPUT / "script-package.md", render_script_package(selected))
    write_text(OUTPUT / "chain-report.md", render_chain_report(selected, candidates, config))

    print(f"已生成内容对标全链路报告：{OUTPUT / 'chain-report.md'}")
    print(f"已生成样本准入卡：{OUTPUT / 'manual-workbench' / '01-samples' / (selected.sample_id + '.source-card.md')}")
    print(f"已生成改写脚本包：{OUTPUT / 'script-package.md'}")


if __name__ == "__main__":
    main()
