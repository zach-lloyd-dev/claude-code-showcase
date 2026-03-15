#!/usr/bin/env python3
"""
last48hours - 48-Hour Intelligence Briefing for Zero to Automated.

Usage:
    python3 last48.py <topic> [options]

Options:
    --mode=MODE     Output mode: pulse|signal|both (default: both)
    --depth=DEPTH   Research depth: quick|default|deep (default: default)
    --emit=FORMAT   Output format: compact|json|md|path (default: compact)
    --refresh       Ignore cache, fetch fresh data
    --diagnose      Show source availability and exit
    --debug         Enable verbose logging
"""

import argparse
import json
import os
import signal
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Add lib to path
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from lib import cache, config, dates, dedupe, render, scoring, schema
from lib.sources import hackernews, reddit, tiktok, instagram, web, x, youtube

# ---------------------------------------------------------------------------
# Timeout management
# ---------------------------------------------------------------------------
TIMEOUT_PROFILES = {
    "quick": 60,
    "default": 120,
    "deep": 240,
}


def _install_timeout(seconds: int):
    if hasattr(signal, "SIGALRM"):
        def _handler(signum, frame):
            sys.stderr.write(f"\n[TIMEOUT] Global timeout ({seconds}s) exceeded.\n")
            sys.exit(1)
        signal.signal(signal.SIGALRM, _handler)
        signal.alarm(seconds)


# ---------------------------------------------------------------------------
# Source diagnostics
# ---------------------------------------------------------------------------
def diagnose():
    """Print source availability and exit."""
    sources = config.check_sources()
    print("Last 48 Hours - Source Diagnostics")
    print("=" * 40)
    for name, info in sources.items():
        status = "available" if info["available"] else "not configured"
        method = f" ({info['method']})" if info.get("method") else ""
        print(f"  {name:12s} : {status}{method}")
    print()
    env = config.load_env()
    print("API Keys:")
    for key in ["SCRAPECREATORS_API_KEY", "AUTH_TOKEN", "CT0", "XAI_API_KEY"]:
        val = env.get(key, "")
        status = f"set ({val[:8]}...)" if val else "not set"
        print(f"  {key:25s} : {status}")
    sys.exit(0)


# ---------------------------------------------------------------------------
# Main research pipeline
# ---------------------------------------------------------------------------
def fetch_all_sources(topic: str, from_date: str, to_date: str, depth: str) -> dict:
    """Fetch from all available sources in parallel."""
    env = config.load_env()
    sc_key = env.get("SCRAPECREATORS_API_KEY", "")
    results = {}
    errors = {}

    def _safe(name, fn, *args, **kwargs):
        try:
            return name, fn(*args, **kwargs), None
        except Exception as e:
            return name, [], str(e)

    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = []

        # Always search HN (free)
        futures.append(executor.submit(
            _safe, "hackernews", hackernews.search_hackernews,
            topic, from_date, to_date, depth))

        # Reddit (needs ScrapeCreators)
        if sc_key:
            futures.append(executor.submit(
                _safe, "reddit", reddit.search_reddit,
                topic, sc_key, from_date, to_date, depth))

        # X/Twitter (needs Bird auth)
        if env.get("AUTH_TOKEN") and env.get("CT0"):
            futures.append(executor.submit(
                _safe, "x", x.search_x,
                topic, from_date, to_date, depth))

        # YouTube (needs yt-dlp)
        if youtube.is_available():
            futures.append(executor.submit(
                _safe, "youtube", youtube.search_youtube,
                topic, from_date, to_date, depth))

        # TikTok (needs ScrapeCreators)
        if sc_key:
            futures.append(executor.submit(
                _safe, "tiktok", tiktok.search_tiktok,
                topic, sc_key, from_date, to_date, depth))

        # Instagram (needs ScrapeCreators)
        if sc_key:
            futures.append(executor.submit(
                _safe, "instagram", instagram.search_instagram,
                topic, sc_key, from_date, to_date, depth))

        # Web fallback
        futures.append(executor.submit(
            _safe, "web", web.search_web,
            topic, from_date, to_date, depth))

        for future in as_completed(futures):
            name, items, error = future.result()
            results[name] = items
            if error:
                errors[name] = error

    return results, errors


def build_report(topic: str, mode: str, depth: str, refresh: bool = False) -> schema.Report:
    """Build the intelligence briefing report."""
    from_date, to_date = dates.get_date_range(hours=48)

    # Check cache
    if not refresh:
        cache_key = cache.get_cache_key(topic, mode, depth)
        cached_data, cache_age = cache.load_cache_with_age(cache_key)
        if cached_data:
            report = schema.Report.from_dict(cached_data)
            report.from_cache = True
            report.cache_age_hours = cache_age
            return report

    # Fetch from all sources
    results, errors = fetch_all_sources(topic, from_date, to_date, depth)

    # Combine all items
    all_items = []
    source_counts = {}
    for source_name, items in results.items():
        all_items.extend(items)
        source_counts[source_name] = len(items)

    # Deduplicate within sources
    all_items = dedupe.dedupe_items(all_items)

    # Cross-source linking
    dedupe.cross_source_link(all_items)

    # Score based on mode
    if mode == "pulse":
        all_items = scoring.score_items_pulse(all_items)
    elif mode == "signal":
        all_items = scoring.score_items_signal(all_items)
    else:
        # Both: score with pulse, then we'll re-score signal items in render
        all_items = scoring.score_items_pulse(all_items)

    # Sort
    all_items = scoring.sort_items(all_items, mode)

    # Build report
    report = schema.create_report(topic, mode, depth, from_date, to_date)
    report.items = all_items
    report.source_errors = errors
    report.source_counts = source_counts

    # Load profile for personalization
    profile = config.load_profile()
    if profile:
        report.user_role = profile.get("role")
        report.user_industry = profile.get("industry")

    # Save to cache
    cache_key = cache.get_cache_key(topic, mode, depth)
    cache.save_cache(cache_key, report.to_dict())

    return report


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------
def emit_compact(report: schema.Report) -> str:
    """Compact output for Claude to synthesize."""
    user_context = ""
    profile = config.load_profile()
    if profile:
        user_context = config.get_user_context(profile)

    if report.mode == "pulse":
        return render.render_pulse(report)
    elif report.mode == "signal":
        return render.render_signal(report, user_context)
    else:
        return render.render_combined(report, user_context)


def emit_json(report: schema.Report) -> str:
    return json.dumps(report.to_dict(), indent=2)


def emit_md(report: schema.Report) -> str:
    user_context = ""
    profile = config.load_profile()
    if profile:
        user_context = config.get_user_context(profile)
    path = render.write_outputs(report, user_context)
    # Also return the markdown
    with open(path, "r") as f:
        return f.read()


def emit_path(report: schema.Report) -> str:
    user_context = ""
    profile = config.load_profile()
    if profile:
        user_context = config.get_user_context(profile)
    return render.write_outputs(report, user_context)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="48-Hour Intelligence Briefing")
    parser.add_argument("topic", nargs="*", help="Topic to research")
    parser.add_argument("--mode", choices=["pulse", "signal", "both"], default="both")
    parser.add_argument("--depth", choices=["quick", "default", "deep"], default="default")
    parser.add_argument("--emit", choices=["compact", "json", "md", "path"], default="compact")
    parser.add_argument("--refresh", action="store_true", help="Ignore cache")
    parser.add_argument("--diagnose", action="store_true", help="Show source diagnostics")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    if args.debug:
        os.environ["LAST48_DEBUG"] = "1"

    if args.diagnose:
        diagnose()

    topic = " ".join(args.topic)
    if not topic:
        print("Usage: python3 last48.py <topic> [--mode pulse|signal|both] [--depth quick|default|deep]", file=sys.stderr)
        sys.exit(1)

    # Install timeout
    timeout = TIMEOUT_PROFILES.get(args.depth, 120)
    _install_timeout(timeout)

    # Build report
    report = build_report(topic, args.mode, args.depth, args.refresh)

    # Emit output
    emitters = {
        "compact": emit_compact,
        "json": emit_json,
        "md": emit_md,
        "path": emit_path,
    }
    output = emitters[args.emit](report)
    print(output)


if __name__ == "__main__":
    main()
