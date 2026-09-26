from datetime import datetime, timezone

from lineage.dating import TWITTER_EPOCH_MS, DateEvidence, best_date, snowflake_time
from lineage.fingerprint import normalize, similarity
from lineage.tree import Variant, build_tree, diff_words


def d(y, m=1, day=1):
    return datetime(y, m, day, tzinfo=timezone.utc)


def test_normalize_and_similarity():
    assert normalize("“Don’t  PANIC!”") == "dont panic"
    assert similarity("Be the change you wish to see", "be the change you wish to see!") == 1.0
    assert similarity("Be the change you wish to see", "cats are liquid and nobody can stop them") == 0.0


def test_snowflake_roundtrip():
    ms = 1_600_000_000_000
    tweet_id = (ms - TWITTER_EPOCH_MS) << 22 | 12345  # low bits = worker/sequence, ignored
    assert snowflake_time(tweet_id) == datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def test_best_date_prefers_trusted_tier():
    ev = [DateEvidence(d(2010), "metadata"), DateEvidence(d(2015), "archive"), DateEvidence(d(2014), "archive")]
    assert best_date(ev).when == d(2014)
    assert best_date([]) is None


def test_tree_chain_diff_and_gap():
    vs = [
        Variant("c", "Not everything that counts can be counted - Albert Einstein", d(2009)),
        Variant("a", "Not everything that counts can be counted, and not everything counted counts", d(1963)),
        Variant("b", "Not everything that counts can be counted", d(1986)),
        Variant("z", "Totally unrelated claim about lizard people running the post office", d(2020)),
    ]
    by_id = {v.id: v for v in build_tree(vs)}
    assert by_id["a"].parent is None
    assert by_id["b"].parent == "a"
    assert by_id["c"].parent == "b"
    assert by_id["z"].parent is None  # gap / independent origin
    assert {"op": "insert", "old": "", "new": "- Albert Einstein"} in by_id["c"].changes


def test_diff_words_replace():
    assert diff_words("said by Einstein", "said by Gandhi") == [{"op": "replace", "old": "Einstein", "new": "Gandhi"}]


def test_short_quote_attribution_swap_still_links():
    by_id = {v.id: v for v in build_tree([
        Variant("a", "said by Einstein long ago", d(1990)),
        Variant("b", "said by Gandhi long ago", d(2000)),
    ])}
    assert by_id["b"].parent == "a"
    assert by_id["b"].changes == [{"op": "replace", "old": "Einstein", "new": "Gandhi"}]
