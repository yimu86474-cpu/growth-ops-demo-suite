from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "sample-data" / "research_inputs.jsonl"
CONFIG = ROOT / "sample-data" / "workflow_config.json"
REPORT = ROOT / "sample-report" / "content-research-report.md"
TOPICS = ROOT / "sample-report" / "topic-pool.csv"
BRIEF = ROOT / "sample-report" / "creation-brief.md"
PUBLISH = ROOT / "sample-report" / "publish-package.md"
EXPLAIN_DOC = "docs/explain/run_content_research_demo.md"


@dataclass(frozen=True)
class ResearchInput:
    source_id: str
    source_type: str
    sanitized_text: str
    business_scene: str
    audience: str
    evidence_type: str
    repeat_count: int
    visual_evidence: str
    conversion_path: str
    sensitivity: str
    screen_demo: str


@dataclass(frozen=True)
class Candidate:
    input: ResearchInput
    decision: str
    pain: int
    evidence: int
    visual: int
    conversion: int
    effort: int
    total: float
    insight: str
    topic: str
    reason: str


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def as_input(row: dict[str, Any]) -> ResearchInput:
    return ResearchInput(
        source_id=str(row["source_id"]),
        source_type=str(row["source_type"]),
        sanitized_text=str(row["sanitized_text"]),
        business_scene=str(row["business_scene"]),
        audience=str(row["audience"]),
        evidence_type=str(row["evidence_type"]),
        repeat_count=int(row.get("repeat_count", 1)),
        visual_evidence=str(row.get("visual_evidence", "")),
        conversion_path=str(row.get("conversion_path", "")),
        sensitivity=str(row.get("sensitivity", "medium")),
        screen_demo=str(row.get("screen_demo", "no")),
    )


def bounded(value: int) -> int:
    return max(1, min(5, value))


def score_candidate(item: ResearchInput, config: dict[str, Any]) -> Candidate:
    if item.sensitivity.lower() not in {"low", "public_safe"}:
        return Candidate(item, "reject_sensitive", 0, 0, 0, 0, 0, 0, "", "", "敏感等级不适合进入公开演示包。")

    if not item.business_scene or not item.audience:
        return Candidate(item, "reject_incomplete", 0, 0, 0, 0, 0, 0, "", "", "缺少业务场景或目标人群。")

    evidence_map = config["evidence_score"]
    source_map = config["source_score"]
    conversion_map = config["conversion_score"]

    pain = bounded(source_map.get(item.source_type, 3) + min(item.repeat_count, 3) - 1)
    evidence = bounded(evidence_map.get(item.evidence_type, 3))
    visual = 5 if item.screen_demo.lower() in {"yes", "true", "available"} else 3
    conversion = bounded(conversion_map.get(item.conversion_path, 3))
    effort = 4 if item.visual_evidence else 3

    weights = config["score_weights"]
    total = (
        pain * weights["pain"]
        + evidence * weights["evidence"]
        + visual * weights["visual"]
        + conversion * weights["conversion"]
        + effort * weights["effort"]
    )

    insight = build_insight(item)
    topic = build_topic(item)
    decision = "enter_script_queue" if total >= config["script_gate"]["min_total"] and effort >= 3 else "candidate_only"
    reason = "通过脚本门禁。" if decision == "enter_script_queue" else "保留为候选资产，先补证据或画面。"

    return Candidate(item, decision, pain, evidence, visual, conversion, effort, round(total, 2), insight, topic, reason)


def build_insight(item: ResearchInput) -> str:
    if item.source_type == "project_log":
        return "用户真正需要的不是概念解释，而是把真实业务流程拆成输入、判断、输出和安全边界。"
    if item.source_type == "audience_question":
        return "用户卡住的不是工具数量，而是不知道如何把自己的业务问题翻译成 AI 可执行任务。"
    if item.source_type == "review_comment":
        return "评论里的高频问题适合先变成需求卡，再决定是否进入选题和脚本。"
    return "素材需要先判断场景、证据和可视化程度，不能直接进入文案生成。"


def build_topic(item: ResearchInput) -> str:
    if item.source_type == "project_log":
        return "别把 AI 项目包装成概念，先把真实流程做成可复核 demo"
    if item.source_type == "audience_question":
        return "不会写需求给 AI？先用输入、判断、输出三句话说清楚"
    if item.source_type == "review_comment":
        return "评论区的问题不是灵感，是下一条内容的需求证据"
    return "一个素材能不能拍，先看它有没有业务场景和证据"


def write_topics(candidates: list[Candidate]) -> None:
    TOPICS.parent.mkdir(parents=True, exist_ok=True)
    with TOPICS.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["source_id", "decision", "topic", "pain", "evidence", "visual", "conversion", "effort", "total"])
        for item in sorted(candidates, key=lambda x: x.total, reverse=True):
            writer.writerow(
                [
                    item.input.source_id,
                    item.decision,
                    item.topic,
                    item.pain,
                    item.evidence,
                    item.visual,
                    item.conversion,
                    item.effort,
                    f"{item.total:.2f}",
                ]
            )


def selected_candidate(candidates: list[Candidate]) -> Candidate:
    eligible = [item for item in candidates if item.decision == "enter_script_queue"]
    if eligible:
        return sorted(eligible, key=lambda x: x.total, reverse=True)[0]
    return sorted(candidates, key=lambda x: x.total, reverse=True)[0]


def render_report(candidates: list[Candidate], config: dict[str, Any]) -> str:
    generated_at = os.environ.get("DEMO_GENERATED_AT", "2026-06-17 00:00:00 (demo)")
    selected = selected_candidate(candidates)
    decisions: dict[str, int] = {}
    for item in candidates:
        decisions[item.decision] = decisions.get(item.decision, 0) + 1

    lines = [
        "# 内容需求研究报告",
        "",
        f"- 生成时间：{generated_at}",
        f"- 输入样本数：{len(candidates)}",
        f"- 脚本门禁：total >= {config['script_gate']['min_total']}，且 effort >= 3。",
        "- 模式：synthetic data only，不抓取平台、不读取评论原文、不自动发布。",
        "",
        "## 流程对齐",
        "",
        "```text",
        "脱敏输入",
        "  -> 样本准入",
        "  -> 需求洞察",
        "  -> 选题评分",
        "  -> 创作 brief",
        "  -> 创作前提示词",
        "  -> 脚本草稿和发布包",
        "  -> 候选资产反哺",
        "```",
        "",
        "## 决策汇总",
        "",
        "| 决策 | 数量 |",
        "|---|---:|",
    ]
    for decision, count in sorted(decisions.items()):
        lines.append(f"| {decision} | {count} |")

    lines.extend(
        [
            "",
            "## 样本评分",
            "",
            "| source_id | 决策 | 总分 | 需求洞察 | 选题方向 |",
            "|---|---|---:|---|---|",
        ]
    )
    for item in sorted(candidates, key=lambda x: x.total, reverse=True):
        lines.append(f"| {item.input.source_id} | {item.decision} | {item.total:.2f} | {item.insight} | {item.topic} |")

    lines.extend(
        [
            "",
            "## 本轮进入创作队列",
            "",
            f"- source_id：`{selected.input.source_id}`",
            f"- 选题：{selected.topic}",
            f"- 选择理由：{selected.reason}",
            f"- 目标人群：{selected.input.audience}",
            f"- 业务场景：{selected.input.business_scene}",
            "",
            "## 安全边界",
            "",
            "- 输入内容全部为重写后的 synthetic 样例。",
            "- 不保存昵称、头像、联系方式、评论原文、私信原文或真实后台数据。",
            "- 输出只到本地 Markdown/CSV，人确认后才可能进入真实录制和发布。",
        ]
    )
    return "\n".join(lines) + "\n"


def render_brief(candidate: Candidate) -> str:
    return "\n".join(
        [
            "# 创作 Brief",
            "",
            f"- source_id：`{candidate.input.source_id}`",
            f"- 粗选题：{candidate.topic}",
            f"- 目标人群：{candidate.input.audience}",
            f"- 业务场景：{candidate.input.business_scene}",
            "- 内容目标：让用户看到 AI 项目不是概念包装，而是能被拆成可运行、可复核、可控边界的流程。",
            "- 心理路径：先戳中“不会落地”的焦虑，再用流程拆解给确定性，最后引导用户从一个重复工作开始。",
            "- 证据状态：有项目过程证据和可录屏 demo，但公开版本只展示 synthetic 数据。",
            "- 输出规格：短版 60-90 秒用于单条发布；标准版 2-3 分钟用于讲完整流程。",
            "",
            "## 创作前提示词",
            "",
            "请围绕【真实流程怎么变成可复核 AI demo】为【有业务经验但不懂代码的运营/增长负责人】写一条内容。",
            "这条内容要解决的场景是【做了很多 AI 小工具，但不知道怎么证明业务价值】，目标是【把项目从概念包装拉回流程证据】。",
            "采用【焦虑 -> 拆解 -> 可验证 -> 安全边界】推进。",
            "开头要指出：只展示几个 Markdown 不够，真正有价值的是输入、判断、输出和复盘都能跑。",
            "中段用 synthetic demo 说明：样本准入、选题评分、脚本草稿和发布包都能被复核。",
            "禁止搬运真实评论、真实客户、真实后台截图和夸大结果。",
            "输出短版口播、标准版骨架、发布包和候选资产。",
            "",
        ]
    )


def render_publish_package(candidate: Candidate) -> str:
    return "\n".join(
        [
            "# 发布包草稿",
            "",
            "## 短版口播",
            "",
            "很多人做 AI 项目，最后只剩几个好看的说明文档。",
            "但真正能说明能力的，不是文档数量，而是这个流程能不能被别人复核。",
            "我的做法是先把一个真实业务流程拆成四件事：输入是什么、怎么判断、输出什么、人在哪里确认。",
            "比如内容选题这件事，不是让 AI 直接写文案，而是先收集脱敏样本，判断痛点、证据、可视化和转化价值，再决定要不要进入脚本。",
            "这样做出来的 demo 即使没有真实账号，也能看出流程能力；同时不泄露客户、评论、聊天和后台数据。",
            "你先别急着让 AI 写成品，先问自己：这个流程的输入、判断、输出和验收标准分别是什么？",
            "",
            "## 标题",
            "",
            "- 别再把 AI 项目做成说明文档了，先让流程跑起来",
            "- 一个 AI demo 有没有价值，看这四个地方",
            "- 不泄露真实数据，也能证明你的业务流程能力",
            "",
            "## 封面文案",
            "",
            "AI 项目不是文档堆砌",
            "",
            "## 正文",
            "",
            "公开 demo 可以没有真实账号，但不能没有真实流程。输入、判断、输出、人工确认和复盘都能被复核，才算真正能说明能力。",
            "",
            "## 置顶评论",
            "",
            "可以先拿你一个重复工作试试：写出输入、判断、输出、人确认点，再看哪一步最适合交给 AI。",
            "",
            "## 候选资产",
            "",
            f"- 选题资产：{candidate.topic}",
            "- 结构资产：输入 -> 判断 -> 输出 -> 人工确认 -> 复盘",
            "- 反例资产：只有 Markdown，没有可运行输入输出。",
            "",
        ]
    )


def main() -> None:
    with CONFIG.open("r", encoding="utf-8") as file:
        config: dict[str, Any] = json.load(file)

    rows = [as_input(row) for row in load_jsonl(INPUT)]
    candidates = [score_candidate(row, config) for row in rows]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render_report(candidates, config), encoding="utf-8")
    write_topics(candidates)

    selected = selected_candidate(candidates)
    BRIEF.write_text(render_brief(selected), encoding="utf-8")
    PUBLISH.write_text(render_publish_package(selected), encoding="utf-8")

    print(f"已生成内容研究报告：{REPORT}")
    print(f"已生成选题评分表：{TOPICS}")
    print(f"已生成创作 brief：{BRIEF}")
    print(f"已生成发布包草稿：{PUBLISH}")


if __name__ == "__main__":
    main()
