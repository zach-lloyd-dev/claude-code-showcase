"""Data schemas for last48hours skill."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Engagement:
    """Universal engagement metrics."""
    score: Optional[int] = None       # Reddit points
    num_comments: Optional[int] = None
    upvote_ratio: Optional[float] = None
    likes: Optional[int] = None       # X, TikTok, Instagram, Bluesky
    reposts: Optional[int] = None     # X, Bluesky
    replies: Optional[int] = None     # X, Bluesky
    quotes: Optional[int] = None      # X
    views: Optional[int] = None       # YouTube, TikTok, Instagram
    shares: Optional[int] = None      # TikTok

    def total(self) -> int:
        """Sum all non-None engagement metrics."""
        vals = [self.score, self.num_comments, self.likes, self.reposts,
                self.replies, self.quotes, self.views, self.shares]
        return sum(v for v in vals if v is not None)

    def to_dict(self) -> Optional[Dict[str, Any]]:
        d = {}
        for k in ("score", "num_comments", "upvote_ratio", "likes", "reposts",
                   "replies", "quotes", "views", "shares"):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d if d else None


@dataclass
class Comment:
    score: int
    date: Optional[str]
    author: str
    excerpt: str
    url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"score": self.score, "date": self.date,
                "author": self.author, "excerpt": self.excerpt, "url": self.url}


@dataclass
class SubScores:
    relevance: int = 0
    recency: int = 0
    engagement: int = 0
    velocity: int = 0  # New: engagement/time for Pulse mode

    def to_dict(self) -> Dict[str, int]:
        return {"relevance": self.relevance, "recency": self.recency,
                "engagement": self.engagement, "velocity": self.velocity}


@dataclass
class BaseItem:
    """Common fields for all source items."""
    id: str
    source: str                           # "reddit", "x", "youtube", etc.
    title: str = ""
    text: str = ""
    url: str = ""
    author: str = ""
    date: Optional[str] = None
    date_confidence: str = "low"
    engagement: Optional[Engagement] = None
    relevance: float = 0.5
    why_relevant: str = ""
    subs: SubScores = field(default_factory=SubScores)
    score: int = 0
    velocity_score: float = 0.0           # engagement_total / hours_since_posted
    cross_refs: List[str] = field(default_factory=list)
    # Signal mode extras
    content_type: str = ""                # "framework", "contrarian", "announcement", etc.
    signal_strength: int = 0              # 1-5 based on cross_refs count

    def display_title(self) -> str:
        return self.title or self.text[:80]

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "text": self.text,
            "url": self.url,
            "author": self.author,
            "date": self.date,
            "date_confidence": self.date_confidence,
            "engagement": self.engagement.to_dict() if self.engagement else None,
            "relevance": self.relevance,
            "why_relevant": self.why_relevant,
            "subs": self.subs.to_dict(),
            "score": self.score,
            "velocity_score": self.velocity_score,
            "content_type": self.content_type,
            "signal_strength": self.signal_strength,
        }
        if self.cross_refs:
            d["cross_refs"] = self.cross_refs
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseItem":
        eng = None
        if data.get("engagement"):
            eng = Engagement(**data["engagement"])
        subs = SubScores(**data.get("subs", {})) if data.get("subs") else SubScores()
        return cls(
            id=data["id"],
            source=data.get("source", "unknown"),
            title=data.get("title", ""),
            text=data.get("text", ""),
            url=data.get("url", ""),
            author=data.get("author", ""),
            date=data.get("date"),
            date_confidence=data.get("date_confidence", "low"),
            engagement=eng,
            relevance=data.get("relevance", 0.5),
            why_relevant=data.get("why_relevant", ""),
            subs=subs,
            score=data.get("score", 0),
            velocity_score=data.get("velocity_score", 0.0),
            cross_refs=data.get("cross_refs", []),
            content_type=data.get("content_type", ""),
            signal_strength=data.get("signal_strength", 0),
        )


# Source-specific metadata stored in extra_data dict on BaseItem
# We use a single BaseItem class instead of per-source classes for simplicity


@dataclass
class Report:
    """Full intelligence briefing report."""
    topic: str
    mode: str                              # "pulse", "signal", "both"
    depth: str                             # "quick", "default", "deep"
    range_from: str
    range_to: str
    generated_at: str
    items: List[BaseItem] = field(default_factory=list)
    # Per-source error tracking
    source_errors: Dict[str, str] = field(default_factory=dict)
    source_counts: Dict[str, int] = field(default_factory=dict)
    # Cache info
    from_cache: bool = False
    cache_age_hours: Optional[float] = None
    # User profile context
    user_role: Optional[str] = None
    user_industry: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "mode": self.mode,
            "depth": self.depth,
            "range": {"from": self.range_from, "to": self.range_to},
            "generated_at": self.generated_at,
            "items": [i.to_dict() for i in self.items],
            "source_errors": self.source_errors,
            "source_counts": self.source_counts,
            "from_cache": self.from_cache,
            "cache_age_hours": self.cache_age_hours,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Report":
        range_data = data.get("range", {})
        items = [BaseItem.from_dict(i) for i in data.get("items", [])]
        return cls(
            topic=data["topic"],
            mode=data.get("mode", "both"),
            depth=data.get("depth", "default"),
            range_from=range_data.get("from", ""),
            range_to=range_data.get("to", ""),
            generated_at=data["generated_at"],
            items=items,
            source_errors=data.get("source_errors", {}),
            source_counts=data.get("source_counts", {}),
            from_cache=data.get("from_cache", False),
            cache_age_hours=data.get("cache_age_hours"),
        )


def create_report(topic: str, mode: str, depth: str, from_date: str, to_date: str) -> Report:
    return Report(
        topic=topic,
        mode=mode,
        depth=depth,
        range_from=from_date,
        range_to=to_date,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
