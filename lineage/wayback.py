"""Wayback Machine CDX lookups. Indexed by URL, so this *dates* known URLs; it can't search content."""
from datetime import datetime, timezone

import httpx

CDX = "https://web.archive.org/cdx/search/cdx"


def earliest_capture(url: str, client: httpx.Client | None = None) -> datetime | None:
    params = {"url": url, "output": "json", "limit": 1, "fl": "timestamp", "filter": "statuscode:200"}
    c = client or httpx.Client(timeout=30, headers={"User-Agent": "lineage/0.0 (research)"})
    rows = c.get(CDX, params=params).json()  # CDX sorts oldest-first; row 0 is the header
    if len(rows) < 2:
        return None
    return datetime.strptime(rows[1][0], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
