#!/usr/bin/env bash
# Install the YouTube Repurpose skill for Claude Code
set -euo pipefail

SKILL_DIR="$HOME/.claude/skills/youtube-repurpose"

mkdir -p "$SKILL_DIR"
cp SKILL.md "$SKILL_DIR/SKILL.md"

echo "✅ YouTube Repurpose skill installed to $SKILL_DIR"
echo ""
echo "Make sure yt-dlp is installed:"
echo "  brew install yt-dlp    (macOS)"
echo "  pip install yt-dlp     (any platform)"
echo ""
echo "Usage: Open Claude Code and say:"
echo '  repurpose this video: https://www.youtube.com/watch?v=VIDEO_ID'
