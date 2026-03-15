# TikTok Script Writer

> Voice-profiled TikTok scripts in 5 proven formats. One-time onboarding, then just describe topics.

## Trigger Keywords
- "Write a script about [topic]"
- "Turn this idea into a script"
- "Script this for TikTok"
- "Create a script about [topic]"
- "TikTok script"

## Process

### First-Time Setup: Onboarding

If no `voice-profile.md` exists in this skill's directory, run onboarding before writing any scripts.

Ask the user:
1. What's your niche/topic area?
2. Who is your audience?
3. What's your content style? (educational, entertaining, motivational, etc.)
4. Can you share 2-3 examples of your existing content? (URLs, transcripts, or descriptions)

From their answers, generate `voice-profile.md` containing:
- Voice characteristics (tone, vocabulary, energy level)
- Audience profile
- Content patterns and preferences
- Hook styles that match their brand

Save to `~/.claude/skills/tiktok-script-writer/voice-profile.md`

If the user says "update my voice profile", re-run onboarding.

### Script Generation

1. Read `voice-profile.md` for voice context
2. Select the best format for the topic (see Five Formats below)
3. Write the script following the format structure
4. Deliver one sentence per line — ready to read on camera

## The Five Formats

### 1. Extended Metaphor
Takes a complex or intimidating concept and explains it through a relatable comparison. Best for technical topics where the audience might feel lost or skeptical.

### 2. Practical Use Cases
Walks through specific real-world applications of a tool or feature. Best for "what can this actually do for me" content.

### 3. Top X Listicle
Numbered list structure — 3 to 7 items. Best for integrations, recommendations, or collections of tips. Audiences know exactly how much content is coming, which holds retention.

### 4. Tutorial / Setup Guide
Step-by-step walkthrough of how to do something. Best for getting-started content where the viewer wants to take action immediately after watching.

### 5. Big News / Article Summary
Covers a major development, viral article, or macro trend. Leads with the news, unpacks what it means, and frames it as an opportunity.

## Output Structure

Every script follows this structure:
- **Hook** (0-3 seconds) — stops the scroll
- **Curiosity loop** (3-10 seconds) — earns the watch
- **Early CTA** (7-10 seconds) — "Bookmark for later and follow for more [topic]"
- **Value section** — delivers on the hook's promise
- **Closing CTA** — drives comments and engagement

Output is dialogue only. One sentence per line. No timestamps, no stage directions — just the words you say on camera.

## File Structure
```
~/.claude/skills/
  tiktok-script-writer/
    SKILL.md
    voice-profile.md  (generated after onboarding)
```

## Notes
- The skill auto-selects the best format based on the topic. Override by specifying: "Write a listicle about..."
- Voice profile persists across sessions — no re-onboarding needed
- For batch creation: give 5 topics, get 5 scripts
