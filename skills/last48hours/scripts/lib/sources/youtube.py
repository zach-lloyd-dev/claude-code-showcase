"""YouTube search via yt-dlp for last48hours."""

import json
import shutil
import subprocess
import sys
from typing import List

from .. import schema, dates

DEPTH_CONFIG = {"quick": 8, "default": 15, "deep": 30}


def _log(msg: str):
    sys.stderr.write(f"[YT] {msg}\n")
    sys.stderr.flush()


def is_available() -> bool:
    return bool(shutil.which("yt-dlp"))


def search_youtube(
    topic: str,
    from_date: str,
    to_date: str,
    depth: str = "default",
) -> List[schema.BaseItem]:
    """Search YouTube via yt-dlp."""
    if not is_available():
        _log("yt-dlp not installed")
        return []

    count = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["default"])
    _log(f"Searching for '{topic}' (count={count})")

    items = []
    try:
        # yt-dlp search -- flat-playlist is fast but has no upload_date
        # so we skip date filtering and accept all results (they're relevance-ranked)
        search_query = f"ytsearch{count}:{topic}"
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--dump-json",
                "--no-warnings",
                search_query,
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )

        if result.returncode != 0 and not result.stdout:
            _log(f"yt-dlp search failed: {result.stderr[:200]}")
            return []

        for i, line in enumerate(result.stdout.strip().split("\n")):
            if not line.strip():
                continue
            try:
                video = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Parse date (may be None with --flat-playlist)
            date_str = video.get("upload_date")
            if date_str and len(date_str) == 8:
                date_str = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
            else:
                date_str = None  # unknown date, still include

            # Filter to 72h window only if we have a date
            if date_str and not dates.is_within_window(date_str, hours=72):
                continue

            eng = schema.Engagement(
                views=video.get("view_count"),
                likes=video.get("like_count"),
                num_comments=video.get("comment_count"),
            )

            vid_id = video.get("id", "")
            desc = video.get("description") or ""
            items.append(schema.BaseItem(
                id=f"YT{i + 1}",
                source="youtube",
                title=video.get("title") or "",
                text=desc[:200],
                url=f"https://youtube.com/watch?v={vid_id}" if vid_id else video.get("url", ""),
                author=video.get("channel") or video.get("uploader") or "",
                date=date_str,
                date_confidence="high",
                engagement=eng,
                relevance=max(0.4, 1.0 - (i * 0.03)),
                why_relevant=f"YouTube video by {video.get('channel', 'unknown')}",
            ))

        _log(f"Found {len(items)} videos")

    except subprocess.TimeoutExpired:
        _log("yt-dlp search timed out")
    except Exception as e:
        _log(f"YouTube search error: {e}")

    return items
