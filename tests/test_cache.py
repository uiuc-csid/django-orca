from django.core.cache import cache

from django_orca.utils import cache_prefix, clear_cache, orca_cache


def test_clear_cache_keeps_other_keys():
    cache.set("unrelated", "value")
    key = "{}-permission-test".format(cache_prefix())
    orca_cache().set(key, "cached")

    clear_cache()

    assert cache.get("unrelated") == "value"
    assert cache_prefix() not in key
    assert orca_cache().get("{}-permission-test".format(cache_prefix())) is None


def test_clear_cache_recovers_from_missing_generation():
    orca_cache().clear()
    clear_cache()
    first = cache_prefix()
    clear_cache()
    assert cache_prefix() != first
