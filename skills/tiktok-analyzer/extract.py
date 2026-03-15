#!/usr/bin/env python3
"""TikTok video metadata and transcript extraction.

Usage:
    python3 extract.py <tiktok_url>

Outputs JSON with video metadata, engagement metrics, and transcript.
Requires: yt-dlp, optionally whisper + ffmpeg for videos without captions.
"""

import json
import subprocess
import sys
import os
import tempfile


def get_metadata(url: str) -> dict:
    """Extract video metadata via yt-dlp."""
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-download", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr}")
    return json.loads(result.stdout)


def get_captions(url: str, tmpdir: str) -> str | None:
    """Try to extract existing captions."""
    result = subprocess.run(
        ["yt-dlp", "--write-auto-sub", "--sub-lang", "en",
         "--skip-download", "--sub-format", "vtt",
         "-o", os.path.join(tmpdir, "%(id)s"), url],
        capture_output=True, text=True
    )
    # Look for .vtt file
    for f in os.listdir(tmpdir):
        if f.endswith(".vtt"):
            with open(os.path.join(tmpdir, f)) as fh:
                return fh.read()
    return None


def transcribe_with_whisper(url: str, tmpdir: str) -> str | None:
    """Download audio and transcribe with Whisper."""
    audio_path = os.path.join(tmpdir, "audio.mp3")
    result = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3",
         "-o", audio_path, url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None

    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result.get("text", "")
    except ImportError:
        print("whisper not installed, skipping transcription", file=sys.stderr)
        return None


def calculate_engagement(meta: dict) -> float:
    """Calculate engagement rate from metrics."""
    views = meta.get("view_count", 0)
    if views == 0:
        return 0.0
    likes = meta.get("like_count", 0)
    comments = meta.get("comment_count", 0)
    shares = meta.get("repost_count", 0)
    # TikTok doesn't always expose bookmarks via yt-dlp
    return round((likes + comments + shares) / views * 100, 2)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract.py <tiktok_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    # Get metadata
    meta = get_metadata(url)

    # Extract key fields
    report = {
        "creator": meta.get("uploader", "Unknown"),
        "creator_id": meta.get("uploader_id", ""),
        "title": meta.get("title", ""),
        "duration": meta.get("duration", 0),
        "view_count": meta.get("view_count", 0),
        "like_count": meta.get("like_count", 0),
        "comment_count": meta.get("comment_count", 0),
        "share_count": meta.get("repost_count", 0),
        "upload_date": meta.get("upload_date", ""),
        "hashtags": meta.get("tags", []),
        "engagement_rate": calculate_engagement(meta),
    }

    # Get transcript
    with tempfile.TemporaryDirectory() as tmpdir:
        transcript = get_captions(url, tmpdir)
        if not transcript:
            transcript = transcribe_with_whisper(url, tmpdir)

    report["transcript"] = transcript or "No transcript available"

    # Calculate words per minute if we have a transcript
    if transcript and report["duration"] > 0:
        word_count = len(transcript.split())
        report["words_per_minute"] = round(word_count / (report["duration"] / 60))
    else:
        report["words_per_minute"] = None

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
