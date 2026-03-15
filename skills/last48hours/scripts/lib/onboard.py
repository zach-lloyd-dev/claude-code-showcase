"""Onboarding questionnaire for last48hours.

This module generates the onboarding prompts. The actual interaction
is handled by SKILL.md using AskUserQuestion tool.
"""

from typing import Dict, List, Optional

from . import config


WELCOME_TEXT = """Welcome to Last 48 Hours -- your personalized intelligence briefing.
Built by Zero to Automated.

Let me set you up (takes ~60 seconds). You can skip any question
by typing "skip" or pressing Enter. You can edit these anytime with /last48 --setup."""

QUESTIONS = [
    {
        "key": "role",
        "prompt": "1. What's your role? (e.g., \"AI automation consultant\", \"marketing agency owner\")\n   Type \"skip\" or press Enter to leave blank.",
        "help": "Helps filter which signals are relevant to your work.",
    },
    {
        "key": "industry",
        "prompt": "2. What industry or niche are you in? (e.g., \"AI/automation\", \"real estate\", \"fitness\")\n   Skip if not applicable.",
        "help": "Used to weight topic relevance in your briefings.",
    },
    {
        "key": "audience",
        "prompt": "3. Who's your target audience? (e.g., \"small business owners\", \"B2B SaaS buyers\")\n   Skip if you're not creating content.",
        "help": "Powers the 'Why this matters to you' personalization in Signal mode.",
    },
    {
        "key": "platforms",
        "prompt": "4. What platforms do you create content on? (comma-separated, or \"skip\")\n   Options: linkedin, x, youtube, tiktok, newsletter, blog, podcast",
        "help": "Used to suggest format-appropriate content ideas in Calendar Seeds.",
        "type": "list",
    },
    {
        "key": "competitors",
        "prompt": "5. Name 1-3 competitors or people you follow for ideas: (or \"skip\")",
        "help": "Feeds into supplementary search queries to track what they're posting.",
        "type": "list",
    },
    {
        "key": "goal",
        "prompt": "6. What's your primary goal?\n   a) Find content ideas  b) Stay ahead of trends  c) Competitive intel  d) All  e) Skip",
        "help": "Adjusts which mode (Pulse vs Signal) gets more weight by default.",
        "type": "choice",
        "choices": {"a": "content_ideas", "b": "trends", "c": "competitive_intel", "d": "all", "e": None},
    },
]

API_KEY_TEXT = """Now let's check your data sources. The more sources, the better your briefings.

Required (at least one):
  SCRAPECREATORS_API_KEY -- Powers Reddit, TikTok, Instagram search
     Get yours: https://scrapecreators.com (sign up -> API Keys)

Optional (recommended):
  AUTH_TOKEN + CT0 -- X/Twitter search (from browser cookies)
  XAI_API_KEY -- X/Twitter fallback (https://console.x.ai/)

Free (no key needed):
  YouTube (uses yt-dlp)
  Hacker News (public API)"""


def parse_answer(raw: str, question: Dict) -> Optional[any]:
    """Parse a user's answer based on question type."""
    raw = raw.strip()
    if not raw or raw.lower() == "skip":
        return None

    qtype = question.get("type", "text")

    if qtype == "list":
        items = [item.strip().strip('"').strip("'") for item in raw.split(",")]
        return [i for i in items if i] or None

    if qtype == "choice":
        choices = question.get("choices", {})
        return choices.get(raw.lower(), raw)

    return raw


def build_profile(answers: Dict[str, any]) -> Dict[str, any]:
    """Build a profile dict from questionnaire answers."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return {
        "role": answers.get("role"),
        "industry": answers.get("industry"),
        "audience": answers.get("audience"),
        "platforms": answers.get("platforms", []),
        "competitors": answers.get("competitors", []),
        "goal": answers.get("goal"),
        "created": now,
        "updated": now,
    }


def format_health_check(sources: Dict) -> str:
    """Format source health check output."""
    lines = ["Checking your sources..."]
    for name, info in sources.items():
        if info["available"]:
            method = info.get("method", "")
            lines.append(f"  {name.capitalize()} ({method}) -- working")
        else:
            lines.append(f"  {name.capitalize()} -- not configured")

    available = sum(1 for v in sources.values() if v["available"])
    total = len(sources)
    lines.append(f"\nYou're set up with {available}/{total} sources. Run /last48 --setup anytime to add more.")
    return "\n".join(lines)


def format_profile(profile: Dict) -> str:
    """Format profile for display."""
    lines = ["## Your Profile", ""]
    for key, value in profile.items():
        if key in ("created", "updated"):
            continue
        display = value if value is not None else "(not set)"
        if isinstance(display, list):
            display = ", ".join(display) if display else "(not set)"
        lines.append(f"- **{key.capitalize()}**: {display}")
    lines.append("")
    lines.append(f"*Last updated: {profile.get('updated', 'unknown')}*")
    lines.append(f"*Profile: {config.PROFILE_FILE}*")
    return "\n".join(lines)
