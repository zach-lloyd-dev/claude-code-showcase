# Last 48 Hours - Intelligence Briefing

**Built by Zero to Automated**

Your personalized 48-hour intelligence briefing. Two modes:

- **Pulse** -- What just happened (breaking news, velocity-scored)
- **Signal** -- Your content edge (insights, frameworks, contrarian takes)

## Quick Start

```bash
# Install (one command)
git clone https://github.com/leroyblacksheep/last48hours.git ~/.claude/skills/last48hours

# First run triggers onboarding
/last48 AI automation

# Or jump straight in
/last48 --pulse AI agents
/last48 --signal content marketing
```

## Usage

```
/last48 <topic>                    # Both modes (Pulse + Signal)
/last48 --pulse <topic>            # Breaking news only
/last48 --signal <topic>           # Content insights only
/last48 --quick <topic>            # Faster, fewer sources
/last48 --deep <topic>             # More thorough research
/last48 --setup                    # Re-run onboarding
/last48 --profile                  # View your profile
/last48 --health                   # Check data source status
```

## Data Sources

| Source     | API Key Needed          | Free? |
|------------|-------------------------|-------|
| Hacker News | None                  | Yes   |
| YouTube    | None (uses yt-dlp)      | Yes   |
| Reddit     | SCRAPECREATORS_API_KEY  | Freemium |
| TikTok     | SCRAPECREATORS_API_KEY  | Freemium |
| Instagram  | SCRAPECREATORS_API_KEY  | Freemium |
| X/Twitter  | AUTH_TOKEN + CT0        | Free (browser cookies) |
| Web        | None (uses bss-search)  | Yes   |

## API Key Setup

Add to `~/.env.local`:

```bash
# ScrapeCreators - powers Reddit, TikTok, Instagram (one key, all three)
export SCRAPECREATORS_API_KEY="your_key_here"

# X/Twitter - from browser cookies (optional)
export AUTH_TOKEN="your_token"
export CT0="your_ct0"

# X/Twitter fallback (optional)
export XAI_API_KEY="your_key"
```

## How It Works

1. Searches 5-7 platforms in parallel (takes 30-90 seconds)
2. Deduplicates and cross-links items across platforms
3. Scores items based on mode:
   - **Pulse**: Velocity scoring (engagement / hours since posted)
   - **Signal**: Relevance scoring with cross-platform amplification
4. Generates personalized briefing based on your profile
5. Caches results for 4 hours (48h window needs fresh data)

## Personalization

On first run, you'll answer 4-6 quick questions about your role, industry,
audience, and content platforms. Every answer is optional.

The more you share, the better the personalization:
- **Why this matters to you** sections in Signal mode
- **Content Calendar Seeds** tailored to your platforms
- Topic filtering based on your industry

Edit anytime: `~/.config/last48hours/profile.yaml`

## Output

Reports save to `~/Documents/Z Brain/04_published/last48hours/`:
- `briefing.md` -- The formatted briefing
- `report.json` -- Raw data for programmatic access

## Updates

Auto-update check runs on session start. Pull when notified:

```bash
git -C ~/.claude/skills/last48hours pull
```
