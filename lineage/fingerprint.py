"""Text fingerprinting: normalize -> word shingles -> Jaccard similarity."""
import re
import unicodedata


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[‘’“”\"']", "", text)  # drop quotes/apostrophes: don't -> dont
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def shingles(text: str, k: int = 2) -> set[str]:
    words = normalize(text).split()
    if len(words) < k:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def similarity(a: str, b: str, k: int = 2) -> float:
    # k=2 not 3: quotes are short, and a single swapped word in a 6-word quote must still match.
    # ponytail: exact Jaccard is O(n^2) across variants; switch to datasketch MinHash+LSH past ~2k candidates
    sa, sb = shingles(a, k), shingles(b, k)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)
