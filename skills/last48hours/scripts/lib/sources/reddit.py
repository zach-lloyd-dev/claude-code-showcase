"""Reddit search via ScrapeCreators API for last48hours."""

import sys
from typing import Any, Dict, List

from .. import http
from .. import schema, dates

SCRAPECREATORS_BASE = "https://api.scrapecreators.com/v1/reddit"

DEPTH_CONFIG = {
    "quick": {"global_searches": 1, "subreddit_searches": 1, "timeframe": "day"},
    "default": {"global_searches": 2, "subreddit_searches": 2, "timeframe": "day"},
    "deep": {"global_searches": 3, "subreddit_searches": 3, "timeframe": "week"},
}


def _log(msg: str):
    sys.stderr.write(f"[Reddit] {msg}\n")
    sys.stderr.flush()


def _headers(token: str) -> Dict[str, str]:
    return {"x-api-key": token, "Content-Type": "application/json"}


def search_reddit(
    topic: str,
    api_key: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[schema.BaseItem]:
    """Search Reddit via ScrapeCreators and return normalized items."""
    if not api_key:
        return []

    cfg = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    _log(f"Searching for '{topic}' (depth={depth})")

    items = []
    try:
        # Global search
        resp = http.post(
            f"{SCRAPECREATORS_BASE}/search",
            json_data={
                "query": topic,
                "timeframe": cfg["timeframe"],
                "sort": "relevance",
                "limit": 25 if depth == "deep" else 15,
            },
            headers=_headers(api_key),
            timeout=60,
        )

        posts = resp.get("data", resp.get("posts", []))
        if isinstance(posts, list):
            for i, post in enumerate(posts):
                eng = schema.Engagement(
                    score=post.get("score") or post.get("ups", 0),
                    num_comments=post.get("num_comments", 0),
                    upvote_ratio=post.get("upvote_ratio"),
                )

                date_str = None
                if post.get("created_utc"):
                    date_str = dates.parse_date(str(post["created_utc"]))
                    if date_str:
                        date_str = date_str.date().isoformat()

                # Filter to 48h window
                if date_str and not dates.is_within_window(date_str, hours=72):
                    continue

                subreddit = post.get("subreddit", post.get("subreddit_name_prefixed", ""))
                if subreddit.startswith("r/"):
                    subreddit = subreddit[2:]

                items.append(schema.BaseItem(
                    id=f"R{i + 1}",
                    source="reddit",
                    title=post.get("title", ""),
                    text=post.get("selftext", "")[:300],
                    url=post.get("url", f"https://reddit.com{post.get('permalink', '')}"),
                    author=f"r/{subreddit}",
                    date=date_str,
                    date_confidence=dates.get_date_confidence(date_str, from_date, to_date),
                    engagement=eng,
                    relevance=max(0.3, 1.0 - (i * 0.03)),
                    why_relevant=f"Reddit discussion in r/{subreddit}",
                ))

        _log(f"Found {len(items)} posts")

    except http.HTTPError as e:
        _log(f"Search failed: {e}")
    except Exception as e:
        _log(f"Search error: {e}")

    return items
