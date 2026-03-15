---
name: last48hours
version: "1.0.0"
description: "48-Hour Intelligence Briefing. Also triggered by '/last48', 'last 48 hours', 'what happened in'. Two modes: Pulse (breaking news) and Signal (content edge). Built by Zero to Automated."
argument-hint: '/last48 AI agents, /last48 --pulse content marketing, /last48 --signal automation tools'
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
homepage: https://github.com/leroyblacksheep/last48hours
repository: https://github.com/leroyblacksheep/last48hours
author: Zero to Automated
license: MIT
user-invocable: true
metadata:
  openclaw:
    emoji: "⚡"
    requires:
      optionalEnv:
        - SCRAPECREATORS_API_KEY
        - AUTH_TOKEN
        - CT0
        - XAI_API_KEY
      bins:
        - python3
    files:
      - "scripts/*"
    tags:
      - intelligence
      - research
      - trends
      - content
      - pulse
      - signal
---

# Last 48 Hours v1.0: Intelligence Briefing

> **Built by Zero to Automated.** Your personalized 48-hour intelligence briefing with two modes: Pulse (what just happened) and Signal (your content edge).

Research ANY topic across Reddit, X, YouTube, TikTok, Instagram, Hacker News, and the web. Surface what's breaking NOW and turn signals into content ideas.

## STEP 0: Parse Flags and Intent

Parse the user's input for:

1. **MODE FLAG**:
   - `--pulse` → Pulse mode only (breaking news, velocity-scored)
   - `--signal` → Signal mode only (insights, content edge)
   - `--setup` → Re-run onboarding questionnaire (go to STEP 1)
   - `--profile` → Show current profile (go to PROFILE DISPLAY)
   - `--health` → Show source health check (go to HEALTH CHECK)
   - No flag → Both modes (default)

2. **DEPTH FLAG**:
   - `--quick` → Faster, fewer sources
   - `--deep` → More thorough research
   - No flag → Default depth

3. **TOPIC**: Everything that isn't a flag

4. **REFRESH**: `--refresh` → Ignore cache

**Store variables:**
- `MODE = pulse | signal | both`
- `DEPTH = quick | default | deep`
- `TOPIC = [extracted topic]`
- `REFRESH = true | false`

## STEP 1: Check for Profile (First-Run Onboarding)

Check if user profile exists:

```bash
test -f ~/.config/last48hours/profile.yaml && echo "EXISTS" || echo "MISSING"
```

### If MISSING (or --setup flag): Run Onboarding

Use AskUserQuestion for each question. Every answer is optional (skip = Enter or "skip").

**Display welcome:**
```
Welcome to Last 48 Hours -- your personalized intelligence briefing.
Built by Zero to Automated.

Let me set you up (takes ~60 seconds). You can skip any question
by typing "skip" or pressing Enter. Edit anytime with /last48 --setup.
```

**Ask questions one at a time via AskUserQuestion:**

1. "What's your role? (e.g., 'AI automation consultant', 'marketing agency owner') — or skip"
2. "What industry or niche? (e.g., 'AI/automation', 'real estate', 'fitness') — or skip"
3. "Who's your target audience? (e.g., 'small business owners', 'B2B SaaS buyers') — or skip"
4. "What platforms do you create content on?" — Use AskUserQuestion with multiSelect: true and these 4 options:
   - "LinkedIn, X, YouTube" (description: "Top professional/creator platforms")
   - "TikTok, Instagram, Facebook" (description: "Top social media platforms")
   - "Newsletter, Blog, Podcast" (description: "Long-form content platforms")
   - "All of the above" (description: "All 9 platforms listed above")
   Users can also select "Other" to type additional platforms. Combine all selected platforms into a single list for the profile.
5. "Name 1-3 competitors or people you follow for ideas — or skip"
6. "Primary goal? a) Content ideas  b) Trends  c) Competitive intel  d) All  e) Skip"

**After collecting answers**, save profile:

```bash
mkdir -p ~/.config/last48hours
cat > ~/.config/last48hours/profile.yaml << 'PROFILE'
# Last 48 Hours - User Profile
# Edit anytime, or run /last48 --setup

role: "{ROLE or null}"
industry: "{INDUSTRY or null}"
audience: "{AUDIENCE or null}"
platforms: [{PLATFORMS_LIST}]
competitors: [{COMPETITORS_LIST}]
goal: "{GOAL or null}"
created: "{TODAY_DATE}"
updated: "{TODAY_DATE}"
PROFILE
```

**Then run health check:**

```bash
python3 ~/.claude/skills/last48hours/scripts/last48.py --diagnose
```

Display results in a clean format:
```
Checking your sources...
  ✅ Hacker News (Algolia) — working
  ✅ YouTube (yt-dlp) — working
  [status for each source based on diagnose output]

You're set up with N/7 sources. Ready to go!
```

If `--setup` was the only flag (no topic), stop here. Otherwise continue to STEP 2.

### If EXISTS: Load profile context

```bash
cat ~/.config/last48hours/profile.yaml
```

Store as `USER_CONTEXT` for personalization in output.

## STEP 2: Run Research

**Display to user:**
```
Researching "{TOPIC}" across all available sources (last 48 hours)...
Mode: {MODE} | Depth: {DEPTH}
```

**Run the Python orchestrator:**

```bash
python3 ~/.claude/skills/last48hours/scripts/last48.py "{TOPIC}" --mode={MODE} --depth={DEPTH} --emit=compact {--refresh if REFRESH}
```

This runs all source searches in parallel and returns scored, deduplicated results.

## STEP 3: Supplement with WebSearch

After the Python script returns, use the WebSearch tool to fill gaps:

1. Search: `"{TOPIC}" latest news last 48 hours`
2. If user has competitors in profile, search: `"{COMPETITOR}" {TOPIC}` for each competitor
3. Add any new findings to the briefing context

## STEP 4: Synthesize and Present

### If MODE = "pulse" or "both":

Present the **Pulse** section:

```markdown
# 48-Hour Pulse: {TOPIC}

🔴 **[Major: {headline}]** — {1-line summary}. Sources: {sources with time ago}
🟡 **[Notable: {headline}]** — {1-line summary}. Sources: {sources with time ago}
🟢 **[Update: {headline}]** — {1-line summary}. Sources: {sources with time ago}

## Quick Takes
- {Insight synthesized from cross-platform signals}
- {Pattern you noticed across sources}
- {What this means for the near future}
```

**Scoring key for Pulse:**
- 🔴 Major = score >= 75 OR velocity > 200 OR 3+ cross-platform refs
- 🟡 Notable = score >= 50 OR velocity > 100 OR 2 cross-platform refs
- 🟢 Update = everything else worth mentioning

### If MODE = "signal" or "both":

Present the **Signal** section:

```markdown
# 48-Hour Signal: {TOPIC}

### 1. {Signal title}
**The signal**: {2-3 sentence summary of what's happening}
**Why this matters to you**: {Personalized to USER_CONTEXT — role, audience, industry}
**Content angle**: {Specific post/video idea they could create}
**Signal strength**: {"xxxxx" for 5 platforms, "xx" for 2, etc.}

### 2. {Signal title}
...

## Content Calendar Seeds
1. [{Platform from profile}] {Post idea based on Signal #1}
2. [{Platform from profile}] {Post idea based on Signal #2}
3. [{Platform from profile}] {Idea based on emerging pattern}
```

**Signal ranking:**
- Prioritize items with 3+ cross-platform references (STRONG SIGNAL badge)
- Frameworks, methodologies, contrarian takes get boosted
- Personalize "Why this matters" using role + audience + industry from profile
- If no profile exists, skip personalization sections (still valuable, just not tailored)

### Source Stats Block (always include at end):

```
---
Sources: {emoji tree showing what was searched}
  ✅ Reddit: {N} threads | ✅ HN: {N} stories | ✅ YouTube: {N} videos
  ✅ X: {N} posts | ❌ TikTok: no key | ⏭️ Instagram: skipped
Cache: {fresh | Xh old} | Depth: {depth} | Mode: {mode}
```

## STEP 5: Save Output

```bash
python3 ~/.claude/skills/last48hours/scripts/last48.py "{TOPIC}" --mode={MODE} --depth={DEPTH} --emit=md
```

Tell user: "Briefing saved to ~/Documents/Z Brain/04_published/last48hours/briefing.md"

## PROFILE DISPLAY (--profile flag)

```bash
cat ~/.config/last48hours/profile.yaml
```

Format and display cleanly. Remind user they can edit the file directly or run `--setup`.

## HEALTH CHECK (--health flag)

```bash
python3 ~/.claude/skills/last48hours/scripts/last48.py --diagnose
```

Display with emoji status indicators.

## Graceful Degradation

1. **Full profile**: All personalization active. "Why this matters to you" + "Content Calendar Seeds" fully tailored.
2. **No profile, has CLAUDE.md**: Read whatever context is available. Partial personalization.
3. **No profile, no context**: Pure signal-strength ranking. No personalization sections. Still valuable. Prompt user to run `--setup`.

## CRITICAL RULES

1. **48-hour window is strict for Pulse mode.** Items older than 48h are excluded. Signal mode can surface older items if they're newly gaining traction.
2. **Velocity over raw engagement for Pulse.** 500 likes in 2 hours >> 5000 likes in 48 hours.
3. **Cross-platform signals are gold.** If something appears on Reddit + HN + X = STRONG SIGNAL. Always highlight.
4. **Every answer in onboarding is optional.** The skill works with zero profile. More answers = better results.
5. **4-hour cache TTL.** 48-hour window needs fresher data than a 30-day tool.
6. **No time estimates.** Don't say "this will take X minutes."
7. **ZTA branding.** This is a Zero to Automated tool. References to "Zero to Automated" or "ZTA" are appropriate.

## Security & Permissions

- Reads public web/platform data only
- API keys from user's `~/.env.local` (already sourced by shell)
- Profile stored locally at `~/.config/last48hours/profile.yaml`
- Output saved to `~/Documents/Z Brain/04_published/last48hours/`
- No data sent to external services beyond the search APIs
- Cache stored at `~/.cache/last48hours/`
