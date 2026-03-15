# YouTube Repurpose

> Paste a YouTube URL, get 4 ready-to-post content formats in one response.

## Trigger Keywords
- "repurpose this video"
- "turn this into social posts"
- "make social content from this"
- Any message containing a YouTube URL (youtube.com, youtu.be)

## Dependencies
- **yt-dlp** — for transcript extraction (`brew install yt-dlp` or `pip install yt-dlp`)
- Falls back to web scraping if yt-dlp is not installed

## Process

### Step 1: Extract Transcript
Run yt-dlp to pull the transcript from the provided YouTube URL:
```bash
yt-dlp --write-auto-sub --sub-lang en --skip-download --sub-format vtt -o "/tmp/%(id)s" "VIDEO_URL"
```
If yt-dlp fails or isn't installed, attempt web scraping. If all methods fail, ask the user to paste the transcript manually.

### Step 2: Analyze Content
Read the transcript and identify:
- Core topic and key takeaways
- Quotable moments and strong phrases
- Story beats and emotional peaks
- Data points, statistics, or concrete examples

### Step 3: Generate Four Formats

**Format 1: TikTok Script** (150-200 words)
- Hook in first sentence (pattern interrupt, bold claim, or question)
- One core idea only
- CTA at the end ("Follow for more [topic]")
- One sentence per line (read-on-camera format)

**Format 2: LinkedIn Post** (150-300 words)
- Opening line earns the "see more" click
- White space between paragraphs (mobile-optimized)
- First-person perspective
- Ends with an engagement question
- No hashtags

**Format 3: X / Twitter**
- If content is simple: single tweet (under 280 chars)
- If content is deep: 5-7 tweet thread
- Thread starts with a hook, ends with a CTA
- Each tweet stands alone but flows as a narrative

**Format 4: Newsletter Section** (200-400 words)
- First-person prose
- One concrete takeaway the reader can act on
- Conversational tone, not academic
- Ends with a transition or soft CTA

### Step 4: Deliver
Present all four formats in a single response, clearly labeled. Each format should be copy-paste ready with no additional editing needed.

## Output Format
```
## 🎬 TikTok Script
[script, one sentence per line]

## 💼 LinkedIn Post
[formatted post]

## 🐦 X / Twitter
[tweet or thread]

## 📧 Newsletter Section
[prose section]
```

## Notes
- If the video is not in English, generate all four formats in the original language, then offer an English translation.
- Private or age-restricted videos cannot be accessed — use public videos only.
- Works with standard YouTube videos, Shorts, and any URL format (youtube.com, youtu.be).
