"""Web search fallback via bss-crawl or bss-search for last48hours."""

import json
import shutil
import subprocess
import sys
from typing import List
from urllib.parse import urlparse

from .. import schema, dates

DEPTH_CONFIG = {"quick": 5, "default": 10, "deep": 20}


def _log(msg: str):
    sys.stderr.write(f"[Web] {msg}\n")
    sys.stderr.flush()


def search_web(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[schema.BaseItem]:
    """Search web via bss-search CLI (SearXNG)."""
    bss_search = shutil.which("bss-search")
    if not bss_search:
        _log("bss-search not found, web search skipped")
        return []

    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    _log(f"Searching for '{topic}' (count={count})")

    items = []
    try:
        result = subprocess.run(
            [bss_search, f"{topic} last 48 hours", "-n", str(count), "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            _log(f"bss-search failed: {result.stderr[:200]}")
            return []

        data = json.loads(result.stdout)
        results = data if isinstance(data, list) else data.get("results", [])

        for i, r in enumerate(results):
            url = r.get("url", "")
            domain = urlparse(url).netloc if url else ""

            items.append(schema.BaseItem(
                id=f"W{i + 1}",
                source="web",
                title=r.get("title", ""),
                text=r.get("content", r.get("snippet", ""))[:300],
                url=url,
                author=domain,
                date=None,  # Web search dates are unreliable
                date_confidence="low",
                engagement=None,
                relevance=max(0.3, 1.0 - (i * 0.05)),
                why_relevant=f"Web result from {domain}",
            ))

        _log(f"Found {len(items)} results")

    except subprocess.TimeoutExpired:
        _log("bss-search timed out")
    except Exception as e:
        _log(f"Web search error: {e}")

    return items
