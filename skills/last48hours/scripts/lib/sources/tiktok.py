"""TikTok search via ScrapeCreators API for last48hours."""

import sys
from typing import List

from .. import http
from .. import schema, dates

SCRAPECREATORS_BASE = "https://api.scrapecreators.com/v1/tiktok"

DEPTH_CONFIG = {"quick": 8, "default": 15, "deep": 30}


def _log(msg: str):
    sys.stderr.write(f"[TikTok] {msg}\n")
    sys.stderr.flush()


def search_tiktok(
    topic: str,
    api_key: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[schema.BaseItem]:
    """Search TikTok via ScrapeCreators."""
    if not api_key:
        return []

    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    _log(f"Searching for '{topic}' (count={count})")

    items = []
    try:
        resp = http.post(
            f"{SCRAPECREATORS_BASE}/search",
            json_data={"query": topic, "limit": count},
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            timeout=90,
        )

        posts = resp.get("data", resp.get("videos", []))
        if isinstance(posts, list):
            for i, post in enumerate(posts):
                # Parse date
                date_str = None
                if post.get("createTime") or post.get("created_at"):
                    raw = str(post.get("createTime") or post.get("created_at"))
                    dt = dates.parse_date(raw)
                    if dt:
                        date_str = dt.date().isoformat()

                if date_str and not dates.is_within_window(date_str, hours=72):
                    continue

                eng = schema.Engagement(
                    views=post.get("playCount", post.get("views")),
                    likes=post.get("diggCount", post.get("likes")),
                    num_comments=post.get("commentCount", post.get("comments")),
                    shares=post.get("shareCount", post.get("shares")),
                )

                author = post.get("author", post.get("authorMeta", {}).get("name", ""))
                text = post.get("desc", post.get("text", ""))

                items.append(schema.BaseItem(
                    id=f"TK{i + 1}",
                    source="tiktok",
                    title="",
                    text=text[:300],
                    url=post.get("webVideoUrl", post.get("url", "")),
                    author=f"@{author}",
                    date=date_str,
                    date_confidence="high" if date_str else "low",
                    engagement=eng,
                    relevance=max(0.4, 1.0 - (i * 0.03)),
                    why_relevant=f"TikTok by @{author}",
                ))

        _log(f"Found {len(items)} videos")

    except http.HTTPError as e:
        _log(f"Search failed: {e}")
    except Exception as e:
        _log(f"Search error: {e}")

    return items
