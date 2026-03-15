"""Output rendering for last48hours (Pulse + Signal templates)."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import dates, schema

OUTPUT_DIR = Path.home() / "Documents" / "Z Brain" / "04_published" / "last48hours"


def ensure_output_dir():
    global OUTPUT_DIR
    env_dir = os.environ.get("LAST48_OUTPUT_DIR")
    if env_dir:
        OUTPUT_DIR = Path(env_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _source_emoji(source: str) -> str:
    return {
        "reddit": "R",
        "x": "X",
        "youtube": "YT",
        "hackernews": "HN",
        "tiktok": "TK",
        "instagram": "IG",
        "web": "W",
    }.get(source, source[:2].upper())


def _xref_sources(item: schema.BaseItem, all_items: list) -> str:
    """Get source names of cross-referenced items."""
    if not item.cross_refs:
        return ""
    ref_sources = set()
    for ref_id in item.cross_refs:
        for other in all_items:
            if other.id == ref_id:
                ref_sources.add(other.source.capitalize())
    if ref_sources:
        return f" [also on: {', '.join(sorted(ref_sources))}]"
    return ""


def _severity_icon(score: int) -> str:
    if score >= 75:
        return "Major"
    elif score >= 50:
        return "Notable"
    return "Update"


def _signal_fire(strength: int) -> str:
    return "x" * min(strength, 5) + " " + f"({strength} platform{'s' if strength != 1 else ''})"


def render_pulse(report: schema.Report) -> str:
    """Render Pulse mode output (breaking news / what just happened)."""
    lines = []
    lines.append(f"# 48-Hour Pulse: {report.topic}")
    lines.append("")
    lines.append(f"*Generated: {report.generated_at[:16]}Z | Window: {report.range_from} to {report.range_to}*")
    lines.append("")

    if report.from_cache:
        age = f"{report.cache_age_hours:.1f}h" if report.cache_age_hours else "cached"
        lines.append(f"**Cached results** ({age}) - use `--refresh` for fresh data")
        lines.append("")

    # Group by severity
    items = sorted(report.items, key=lambda x: -x.score)

    for item in items[:20]:
        age = dates.hours_ago_label(dates.hours_ago(item.date))
        sev = _severity_icon(item.score)
        src = _source_emoji(item.source)

        eng_parts = []
        if item.engagement:
            e = item.engagement
            if e.views is not None:
                eng_parts.append(f"{e.views:,}v")
            if e.likes is not None:
                eng_parts.append(f"{e.likes:,}lk")
            if e.score is not None:
                eng_parts.append(f"{e.score}pts")
            if e.num_comments is not None:
                eng_parts.append(f"{e.num_comments}cmt")
        eng_str = f" [{', '.join(eng_parts)}]" if eng_parts else ""

        title = item.display_title()
        xref = _xref_sources(item, report.items)

        lines.append(f"**[{sev}: {title[:100]}]**")
        lines.append(f"  {item.author} ({age}) | {src}{eng_str}{xref}")
        lines.append(f"  {item.url}")
        if item.velocity_score > 0:
            lines.append(f"  Velocity: {item.velocity_score:.0f} eng/hr")
        lines.append("")

    # Source status
    lines.append("---")
    lines.append("**Sources:**")
    for source, count in sorted(report.source_counts.items()):
        if count > 0:
            lines.append(f"  {source.capitalize()}: {count} items")
    for source, error in report.source_errors.items():
        lines.append(f"  {source.capitalize()}: error - {error}")
    lines.append("")

    return "\n".join(lines)


def render_signal(report: schema.Report, user_context: str = "") -> str:
    """Render Signal mode output (content edge / insights)."""
    lines = []
    lines.append(f"# 48-Hour Signal: {report.topic}")
    lines.append("")
    lines.append(f"*Generated: {report.generated_at[:16]}Z | Window: {report.range_from} to {report.range_to}*")
    if user_context:
        lines.append(f"*Personalized for: {user_context.split(chr(10))[0]}*")
    lines.append("")

    items = sorted(report.items, key=lambda x: -x.score)

    for rank, item in enumerate(items[:15], 1):
        title = item.display_title()
        xref_count = len(item.cross_refs) + 1
        fire = "x" * min(xref_count, 5)

        lines.append(f"### {rank}. {title[:100]}")
        lines.append(f"**The signal**: {item.why_relevant}")
        if item.text and item.text != item.title:
            lines.append(f"  {item.text[:200]}")

        if user_context:
            lines.append(f"**Why this matters to you**: Relevant to your work in {report.user_industry or report.topic}")

        age = dates.hours_ago_label(dates.hours_ago(item.date))
        lines.append(f"**Source**: {item.author} ({age}) | {item.url}")
        lines.append(f"**Signal strength**: {fire} ({xref_count} platform{'s' if xref_count != 1 else ''})")
        lines.append("")

    # Content Calendar Seeds
    lines.append("## Content Calendar Seeds")
    lines.append("")
    for i, item in enumerate(items[:5], 1):
        platform = "LinkedIn" if i % 2 == 1 else "X"
        lines.append(f"{i}. [{platform}] Post idea based on: {item.display_title()[:80]}")
    lines.append("")

    # Source status
    lines.append("---")
    lines.append("**Sources:**")
    for source, count in sorted(report.source_counts.items()):
        if count > 0:
            lines.append(f"  {source.capitalize()}: {count} items")
    lines.append("")

    return "\n".join(lines)


def render_combined(report: schema.Report, user_context: str = "") -> str:
    """Render both Pulse and Signal from same data."""
    pulse = render_pulse(report)
    signal = render_signal(report, user_context)
    return pulse + "\n\n---\n\n" + signal


def write_outputs(report: schema.Report, user_context: str = ""):
    """Write all output files."""
    ensure_output_dir()

    # JSON report
    with open(OUTPUT_DIR / "report.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    # Markdown reports
    mode = report.mode
    if mode == "pulse":
        md = render_pulse(report)
    elif mode == "signal":
        md = render_signal(report, user_context)
    else:
        md = render_combined(report, user_context)

    with open(OUTPUT_DIR / "briefing.md", "w") as f:
        f.write(md)

    return str(OUTPUT_DIR / "briefing.md")
