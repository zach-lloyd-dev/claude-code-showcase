# TikTok Analyzer

> Competitive research: drop a TikTok URL, get metrics, transcript, engagement rate, hook/CTA identification.

## Trigger Keywords
- "Analyze this TikTok"
- "Pull the transcript from this video"
- "What are the stats on this?"
- "Break down this video"
- Any message containing a TikTok URL

## Dependencies
- **yt-dlp** — for video metadata and caption extraction (`pip3 install yt-dlp`)
- **whisper** (optional) — for transcription when captions aren't available (`pip3 install openai-whisper`)
- **ffmpeg** — required by whisper for audio processing (`brew install ffmpeg`)

## Process

### Step 1: Extract Metadata
Use yt-dlp to pull video metadata:
```bash
yt-dlp --dump-json "TIKTOK_URL"
```

Extract:
- Creator name and handle
- View count, like count, comment count, shares, bookmarks
- Video duration and publish date
- Hashtags used

### Step 2: Calculate Engagement Rate
```
engagement_rate = (likes + comments + shares + bookmarks) / views * 100
```

### Step 3: Get Transcript
1. **Try captions first** — grab existing captions from the video (instant)
2. **Fall back to Whisper** — if no captions exist, download audio and run Whisper locally to generate a transcript

### Step 4: Analyze Content
From the transcript, identify:
- **Hook** — the first 3 seconds of dialogue
- **CTA** — the last 10 seconds of dialogue
- **Words per minute** (speaking pace)
- **Full transcript** with timestamps

### Step 5: Generate Report
Format everything into a structured markdown report.

## Output Format
```
## TikTok Analysis Report

**Creator:** @handle (Name)
**Published:** YYYY-MM-DD
**Duration:** X:XX

### Metrics
| Metric | Value |
|--------|-------|
| Views | X |
| Likes | X |
| Comments | X |
| Shares | X |
| Bookmarks | X |
| Engagement Rate | X.XX% |

### Content Analysis
**Hook (0-3s):** "..."
**CTA (last 10s):** "..."
**Speaking Pace:** XXX words/min
**Hashtags:** #tag1 #tag2

### Full Transcript
[timestamped transcript]
```

## Best Use Cases
- **Competitor research** — analyze what hooks, structures, and CTAs top performers use
- **Pattern identification** — run 5-10 videos through it and look for patterns in pacing, hooks, engagement
- **Script benchmarking** — analyze similar videos before writing your own script
- **Content library** — save reports to build a reference library of what works

## Notes
- Captioned videos analyze in under 30 seconds. Whisper transcription takes longer depending on video length.
- Works best paired with the TikTok Script Writer skill: analyze what works, then generate scripts using those patterns.
