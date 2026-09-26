"""Dating candidates: snowflake IDs and choosing the most trustworthy date from mixed evidence."""
from dataclasses import dataclass
from datetime import datetime, timezone

TWITTER_EPOCH_MS = 1288834974657
DISCORD_EPOCH_MS = 1420070400000

# Higher = harder to fake. A platform timestamp is set by the server; an archive capture proves the
# page existed *by* that moment; page metadata and search-engine dates are self-reported.
TRUST = {"platform": 3, "archive": 2, "metadata": 1, "search": 0}


def snowflake_time(snowflake_id: int, epoch_ms: int = TWITTER_EPOCH_MS) -> datetime:
    """Creation time encoded in a Twitter/X or Discord ID. Twitter IDs before ~Nov 2010 aren't snowflakes."""
    return datetime.fromtimestamp(((snowflake_id >> 22) + epoch_ms) / 1000, tz=timezone.utc)


@dataclass(frozen=True)
class DateEvidence:
    when: datetime
    kind: str  # key of TRUST

    def __post_init__(self):
        if self.kind not in TRUST:
            raise ValueError(f"unknown evidence kind {self.kind!r}")


def best_date(evidence: list[DateEvidence]) -> DateEvidence | None:
    """Earliest date within the most trustworthy tier present."""
    # ponytail: tier-first ignores a metadata date that's earlier than the first archive capture (often real).
    # Upgrade: accept metadata when it's < archive date and the site is on an allowlist of honest publishers.
    if not evidence:
        return None
    top = max(TRUST[e.kind] for e in evidence)
    return min((e for e in evidence if TRUST[e.kind] == top), key=lambda e: e.when)
