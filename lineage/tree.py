"""Build the lineage tree: order variants by date, attach each to its most similar earlier variant."""
import difflib
from dataclasses import dataclass, field
from datetime import datetime

from .fingerprint import similarity


@dataclass
class Variant:
    id: str
    text: str
    date: datetime
    url: str = ""
    parent: str | None = None
    score: float = 0.0  # similarity to parent
    changes: list[dict] = field(default_factory=list)


def diff_words(old: str, new: str) -> list[dict]:
    """Word-level edits from old to new: the 'commit' between parent and child."""
    a, b = old.split(), new.split()
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        if op != "equal":
            out.append({"op": op, "old": " ".join(a[i1:i2]), "new": " ".join(b[j1:j2])})
    return out


def build_tree(variants: list[Variant], threshold: float = 0.25) -> list[Variant]:
    """Greedy: parent = most similar strictly-earlier variant above threshold, else a new root.

    A root that isn't the oldest node means either an independent origin or a missing link.
    The UI should show it as a gap, not as proof of independent invention.
    """
    ordered = sorted(variants, key=lambda v: v.date)
    for i, v in enumerate(ordered):
        best, best_score = None, 0.0
        for u in ordered[:i]:
            if u.date == v.date:
                continue
            s = similarity(u.text, v.text)
            if s > best_score:
                best, best_score = u, s
        if best and best_score >= threshold:
            v.parent, v.score, v.changes = best.id, best_score, diff_words(best.text, v.text)
        else:
            v.parent, v.score, v.changes = None, 0.0, []
    return ordered
