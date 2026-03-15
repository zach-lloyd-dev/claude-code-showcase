"""Configuration + user profile loading for last48hours."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    import json

PROFILE_DIR = Path.home() / ".config" / "last48hours"
PROFILE_FILE = PROFILE_DIR / "profile.yaml"
HISTORY_FILE = PROFILE_DIR / "history.yaml"


def load_env() -> Dict[str, str]:
    """Load API keys from environment (already sourced from ~/.env.local by .zshrc)."""
    keys = [
        "SCRAPECREATORS_API_KEY",
        "AUTH_TOKEN", "CT0",
        "XAI_API_KEY",
        "OPENAI_API_KEY",
    ]
    return {k: os.environ.get(k, "") for k in keys}


def load_profile() -> Optional[Dict[str, Any]]:
    """Load user profile from ~/.config/last48hours/profile.yaml."""
    if not PROFILE_FILE.exists():
        return None

    try:
        with open(PROFILE_FILE, "r") as f:
            if HAS_YAML:
                return yaml.safe_load(f) or {}
            else:
                # Fallback: simple YAML-like parsing for basic key: value
                return _parse_simple_yaml(f.read())
    except Exception:
        return None


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Minimal YAML parser for profile files (handles basic key: value pairs)."""
    result = {}
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value.startswith("[") and value.endswith("]"):
                # Simple list parsing
                inner = value[1:-1]
                value = [v.strip().strip('"').strip("'") for v in inner.split(",") if v.strip()]
            elif value.lower() == "null" or value == "~":
                value = None
            result[key] = value
    return result


def save_profile(profile: Dict[str, Any]) -> None:
    """Save user profile."""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_FILE, "w") as f:
        if HAS_YAML:
            yaml.dump(profile, f, default_flow_style=False, sort_keys=False)
        else:
            # Simple YAML-like output
            f.write("# Last 48 Hours - User Profile\n")
            f.write("# Edit anytime, or run /last48 --setup\n\n")
            for k, v in profile.items():
                if v is None:
                    f.write(f"{k}: null\n")
                elif isinstance(v, list):
                    f.write(f"{k}: [{', '.join(str(x) for x in v)}]\n")
                else:
                    f.write(f'{k}: "{v}"\n')


def profile_exists() -> bool:
    return PROFILE_FILE.exists()


def get_user_context(profile: Optional[Dict[str, Any]]) -> str:
    """Build USER_CONTEXT string from profile for injection into prompts."""
    if not profile:
        return ""

    parts = []
    if profile.get("role"):
        parts.append(f"Role: {profile['role']}")
    if profile.get("industry"):
        parts.append(f"Industry: {profile['industry']}")
    if profile.get("audience"):
        parts.append(f"Target audience: {profile['audience']}")
    if profile.get("platforms"):
        platforms = profile["platforms"]
        if isinstance(platforms, list):
            parts.append(f"Content platforms: {', '.join(platforms)}")
        else:
            parts.append(f"Content platforms: {platforms}")
    if profile.get("competitors"):
        comps = profile["competitors"]
        if isinstance(comps, list):
            parts.append(f"Competitors/influences: {', '.join(comps)}")
        else:
            parts.append(f"Competitors/influences: {comps}")
    if profile.get("goal"):
        parts.append(f"Primary goal: {profile['goal']}")

    return "\n".join(parts)


def check_sources() -> Dict[str, Dict[str, Any]]:
    """Check which data sources are available and working."""
    env = load_env()
    sources = {}

    # ScrapeCreators (Reddit, TikTok, Instagram)
    sc_key = env.get("SCRAPECREATORS_API_KEY", "")
    sources["reddit"] = {"available": bool(sc_key), "method": "ScrapeCreators" if sc_key else None}
    sources["tiktok"] = {"available": bool(sc_key), "method": "ScrapeCreators" if sc_key else None}
    sources["instagram"] = {"available": bool(sc_key), "method": "ScrapeCreators" if sc_key else None}

    # X/Twitter
    auth = env.get("AUTH_TOKEN", "")
    ct0 = env.get("CT0", "")
    xai = env.get("XAI_API_KEY", "")
    if auth and ct0:
        sources["x"] = {"available": True, "method": "Bird CLI"}
    elif xai:
        sources["x"] = {"available": True, "method": "xAI API"}
    else:
        sources["x"] = {"available": False, "method": None}

    # YouTube (yt-dlp, free)
    import shutil
    sources["youtube"] = {"available": bool(shutil.which("yt-dlp")), "method": "yt-dlp"}

    # Hacker News (always free)
    sources["hackernews"] = {"available": True, "method": "Algolia API (free)"}

    # Web (bss-crawl or WebSearch fallback)
    sources["web"] = {"available": True, "method": "WebSearch fallback"}

    return sources
