"""Scoring with velocity mode for last48hours.

Two scoring strategies:
- PULSE (velocity-first): engagement_total / max(hours_since_posted, 1)
  A post with 500 likes in 2 hours (velocity=250) ranks above 5000 likes in 48h (velocity=104)
- SIGNAL (relevance-first): Profile relevance weight + cross-platform amplification
"""

import math
from typing import List, Optional

from . import dates, schema

# Pulse mode weights
PULSE_WEIGHT_VELOCITY = 0.45
PULSE_WEIGHT_RECENCY = 0.30
PULSE_WEIGHT_ENGAGEMENT = 0.25

# Signal mode weights
SIGNAL_WEIGHT_RELEVANCE = 0.50
SIGNAL_WEIGHT_ENGAGEMENT = 0.25
SIGNAL_WEIGHT_RECENCY = 0.10
SIGNAL_WEIGHT_CROSS_REF = 0.15

# Cross-platform bonus per additional source
CROSS_REF_BONUS = 15

# Content type boosts for Signal mode
CONTENT_TYPE_BOOST = {
    "framework": 10,
    "methodology": 10,
    "contrarian": 10,
    "data": 8,
    "case_study": 8,
    "tutorial": 5,
    "announcement": 0,
    "opinion": 3,
}


def log1p_safe(x: Optional[int]) -> float:
    if x is None or x < 0:
        return 0.0
    return math.log1p(x)


def compute_velocity(item: schema.BaseItem) -> float:
    """Compute velocity = total_engagement / max(hours_since_posted, 1)."""
    if not item.engagement:
        return 0.0
    total = item.engagement.total()
    if total <= 0:
        return 0.0
    h = dates.hours_ago(item.date)
    if h is None:
        h = 48.0  # Assume worst case for unknown dates
    h = max(h, 0.5)  # Floor at 30 min to avoid division artifacts
    return total / h


def compute_engagement_raw(item: schema.BaseItem) -> float:
    """Compute raw engagement score based on source type."""
    eng = item.engagement
    if not eng:
        return 0.0

    source = item.source
    if source == "reddit":
        return 0.50 * log1p_safe(eng.score) + 0.35 * log1p_safe(eng.num_comments) + 0.15 * (eng.upvote_ratio or 0.5) * 10
    elif source == "x":
        return 0.55 * log1p_safe(eng.likes) + 0.25 * log1p_safe(eng.reposts) + 0.15 * log1p_safe(eng.replies) + 0.05 * log1p_safe(eng.quotes)
    elif source == "youtube":
        return 0.50 * log1p_safe(eng.views) + 0.35 * log1p_safe(eng.likes) + 0.15 * log1p_safe(eng.num_comments)
    elif source in ("tiktok", "instagram"):
        return 0.50 * log1p_safe(eng.views) + 0.30 * log1p_safe(eng.likes) + 0.20 * log1p_safe(eng.num_comments)
    elif source == "hackernews":
        return 0.55 * log1p_safe(eng.score) + 0.45 * log1p_safe(eng.num_comments)
    else:
        return log1p_safe(eng.likes) + log1p_safe(eng.views)


def normalize_to_100(values: List[float]) -> List[float]:
    valid = [v for v in values if v > 0]
    if not valid:
        return [50.0 for _ in values]
    min_val, max_val = min(valid), max(valid)
    range_val = max_val - min_val
    if range_val == 0:
        return [50.0 for _ in values]
    return [((v - min_val) / range_val) * 100 if v > 0 else 25.0 for v in values]


def score_items_pulse(items: List[schema.BaseItem]) -> List[schema.BaseItem]:
    """Score items for Pulse mode (velocity-first)."""
    if not items:
        return items

    # Compute velocities
    velocities = [compute_velocity(item) for item in items]
    vel_norm = normalize_to_100(velocities)

    eng_raw = [compute_engagement_raw(item) for item in items]
    eng_norm = normalize_to_100(eng_raw)

    for i, item in enumerate(items):
        rec = dates.recency_score(item.date, max_hours=48)
        vel = int(vel_norm[i])
        eng = int(eng_norm[i])

        item.velocity_score = velocities[i]
        item.subs = schema.SubScores(
            relevance=int(item.relevance * 100),
            recency=rec,
            engagement=eng,
            velocity=vel,
        )

        overall = (
            PULSE_WEIGHT_VELOCITY * vel +
            PULSE_WEIGHT_RECENCY * rec +
            PULSE_WEIGHT_ENGAGEMENT * eng
        )

        # Cross-ref bonus
        overall += len(item.cross_refs) * 5

        item.score = max(0, min(100, int(overall)))
        item.signal_strength = min(5, len(item.cross_refs) + 1)

    return items


def score_items_signal(items: List[schema.BaseItem]) -> List[schema.BaseItem]:
    """Score items for Signal mode (relevance-first + cross-platform amplification)."""
    if not items:
        return items

    eng_raw = [compute_engagement_raw(item) for item in items]
    eng_norm = normalize_to_100(eng_raw)

    for i, item in enumerate(items):
        rel = int(item.relevance * 100)
        rec = dates.recency_score(item.date, max_hours=48)
        eng = int(eng_norm[i])
        xref = min(100, len(item.cross_refs) * CROSS_REF_BONUS)

        item.subs = schema.SubScores(
            relevance=rel,
            recency=rec,
            engagement=eng,
            velocity=0,
        )

        overall = (
            SIGNAL_WEIGHT_RELEVANCE * rel +
            SIGNAL_WEIGHT_ENGAGEMENT * eng +
            SIGNAL_WEIGHT_RECENCY * rec +
            SIGNAL_WEIGHT_CROSS_REF * xref
        )

        # Content type boost
        ct_boost = CONTENT_TYPE_BOOST.get(item.content_type, 0)
        overall += ct_boost

        item.score = max(0, min(100, int(overall)))
        item.signal_strength = min(5, len(item.cross_refs) + 1)

    return items


def sort_items(items: List[schema.BaseItem], mode: str = "pulse") -> List[schema.BaseItem]:
    """Sort items by score descending."""
    return sorted(items, key=lambda x: (-x.score, -(x.velocity_score if mode == "pulse" else x.relevance)))
