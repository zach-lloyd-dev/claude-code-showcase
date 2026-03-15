"""Hacker News search via Algolia API (free, no auth) for last48hours."""

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlencode

from .. import http
from .. import schema, dates

ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
ALGOLIA_ITEM_URL = "https://hn.algolia.com/api/v1/items"

DEPTH_CONFIG = {"quick": 10, "default": 20, "deep": 40}
ENRICH_LIMITS = {"quick": 3, "default": 5, "deep": 8}


def _log(msg: str):
    if sys.stderr.isatty():
        sys.stderr.write(f"[HN] {msg}\n")
        sys.stderr.flush()


def _strip_html(text: str) -> str:
    import re
    import html
    text = html.unescape(text)
    text = re.sub(r"<p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def search_hackernews(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[schema.BaseItem]:
    """Search HN via Algolia."""
    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    _log(f"Searching for '{topic}' (count={count})")

    # Convert dates to unix timestamps
    from_ts = int(datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    to_ts = int(datetime.strptime(to_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()) + 86400

    params = {
        "query": topic,
        "tags": "story",
        "numericFilters": f"created_at_i>{from_ts},created_at_i<{to_ts}",
        "hitsPerPage": str(count),
    }

    url = f"{ALGOLIA_SEARCH_URL}?{urlencode(params)}"

    items = []
    try:
        response = http.get(url, timeout=30)
        hits = response.get("hits", [])
        _log(f"Found {len(hits)} stories")

        for i, hit in enumerate(hits):
            object_id = hit.get("objectID", "")
            points = hit.get("points") or 0
            num_comments = hit.get("num_comments") or 0
            created_at_i = hit.get("created_at_i")

            date_str = None
            if created_at_i:
                dt = datetime.fromtimestamp(created_at_i, tz=timezone.utc)
                date_str = dt.date().isoformat()

            # Filter to 48h window
            if date_str and not dates.is_within_window(date_str, hours=72):
                continue

            article_url = hit.get("url") or ""
            hn_url = f"https://news.ycombinator.com/item?id={object_id}"

            eng = schema.Engagement(score=points, num_comments=num_comments)

            items.append(schema.BaseItem(
                id=f"HN{i + 1}",
                source="hackernews",
                title=hit.get("title", ""),
                text="",
                url=hn_url,
                author=hit.get("author", ""),
                date=date_str,
                date_confidence="high",
                engagement=eng,
                relevance=max(0.3, 1.0 - (i * 0.02)),
                why_relevant=f"HN discussion ({points}pts, {num_comments} comments)",
            ))

    except Exception as e:
        _log(f"Search failed: {e}")

    # Enrich top stories with comments
    limit = ENRICH_LIMITS.get(depth, ENRICH_LIMITS["default"])
    if items:
        by_points = sorted(range(len(items)), key=lambda i: items[i].engagement.score or 0, reverse=True)
        to_enrich = by_points[:limit]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for idx in to_enrich:
                hn_id = items[idx].url.split("id=")[-1] if "id=" in items[idx].url else ""
                if hn_id:
                    futures[executor.submit(_fetch_comments, hn_id)] = idx

            for future in as_completed(futures):
                idx = futures[future]
                try:
                    insights = future.result(timeout=15)
                    if insights:
                        items[idx].text = " | ".join(insights[:3])
                except Exception:
                    pass

    return items


def _fetch_comments(object_id: str, max_comments: int = 5) -> List[str]:
    """Fetch top comment insights for a story."""
    try:
        data = http.get(f"{ALGOLIA_ITEM_URL}/{object_id}", timeout=15)
        children = data.get("children", [])
        real = [c for c in children if c.get("text") and c.get("author")]
        real.sort(key=lambda c: c.get("points") or 0, reverse=True)

        insights = []
        for c in real[:max_comments]:
            text = _strip_html(c.get("text", ""))
            first = text.split(". ")[0].split("\n")[0][:200]
            if first:
                insights.append(first)
        return insights
    except Exception:
        return []
