"""X/Twitter search via Bird CLI for last48hours."""

import json
import os
import shutil
import subprocess
import sys
from typing import Dict, List, Optional

from .. import schema, dates

DEPTH_CONFIG = {"quick": 10, "default": 25, "deep": 50}


def _log(msg: str):
    sys.stderr.write(f"[X] {msg}\n")
    sys.stderr.flush()


def _find_bird() -> Optional[str]:
    """Find bird binary."""
    # Check common locations
    for path in [
        os.path.expanduser("~/.bun/bin/bird"),
        shutil.which("bird"),
    ]:
        if path and os.path.isfile(path):
            return path
    return None


def _bird_env() -> Dict[str, str]:
    """Build env for Bird subprocess."""
    env = os.environ.copy()
    # Bird needs AUTH_TOKEN and CT0
    return env


def search_x(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[schema.BaseItem]:
    """Search X via Bird CLI."""
    bird = _find_bird()
    if not bird:
        _log("Bird CLI not found")
        return []

    auth_token = os.environ.get("AUTH_TOKEN", "")
    ct0 = os.environ.get("CT0", "")
    if not auth_token or not ct0:
        _log("No AUTH_TOKEN/CT0 credentials")
        return []

    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    _log(f"Searching for '{topic}' via Bird (count={count})")

    items = []
    try:
        # Use Bird search with recency filter
        result = subprocess.run(
            [bird, "search", topic, "--count", str(count), "--json"],
            capture_output=True,
            text=True,
            timeout=60,
            env=_bird_env(),
        )

        if result.returncode != 0:
            _log(f"Bird search failed: {result.stderr[:200]}")
            return []

        # Bird outputs JSON array or object
        data = json.loads(result.stdout)
        tweets = data if isinstance(data, list) else data.get("tweets", data.get("data", []))

        for i, tweet in enumerate(tweets):
            # Parse engagement
            eng = schema.Engagement(
                likes=tweet.get("likes", tweet.get("favorite_count", 0)),
                reposts=tweet.get("retweets", tweet.get("retweet_count", 0)),
                replies=tweet.get("replies", tweet.get("reply_count", 0)),
                quotes=tweet.get("quotes", tweet.get("quote_count", 0)),
                views=tweet.get("views", tweet.get("impression_count")),
            )

            # Parse date
            date_str = tweet.get("date", tweet.get("created_at"))
            if date_str:
                dt = dates.parse_date(date_str)
                if dt:
                    date_str = dt.date().isoformat()

            # Filter to ~48h window (allow some slack)
            if date_str and not dates.is_within_window(date_str, hours=72):
                continue

            handle = tweet.get("author_handle", tweet.get("username", tweet.get("screen_name", "")))
            text = tweet.get("text", tweet.get("full_text", ""))
            tweet_id = tweet.get("id", tweet.get("id_str", f"x{i}"))
            url = tweet.get("url", f"https://x.com/{handle}/status/{tweet_id}")

            items.append(schema.BaseItem(
                id=f"X{i + 1}",
                source="x",
                title="",
                text=text,
                url=url,
                author=f"@{handle}",
                date=date_str,
                date_confidence=dates.get_date_confidence(date_str, from_date, to_date),
                engagement=eng,
                relevance=max(0.3, 1.0 - (i * 0.02)),
                why_relevant=f"X post by @{handle}",
            ))

        _log(f"Found {len(items)} tweets")

    except subprocess.TimeoutExpired:
        _log("Bird search timed out")
    except json.JSONDecodeError as e:
        _log(f"Bird output parse error: {e}")
    except Exception as e:
        _log(f"Bird search error: {e}")

    return items
