from unittest import mock

import pytest
from django.core.cache import cache

from django_orca.utils import (
    _generation_key,
    cache_prefix,
    cache_timeout,
    clear_cache,
    orca_cache,
    string_to_permission,
)


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


def test_clear_cache_stores_generation_without_timeout():
    with mock.patch.object(orca_cache(), "set", wraps=orca_cache().set) as set_:
        clear_cache()
    set_.assert_called_once_with(_generation_key(), mock.ANY, timeout=None)


def test_cache_timeout_setting(settings):
    assert cache_timeout() == 300
    settings.ORCA_SETTINGS = {"CACHE_TIMEOUT": 60}
    assert cache_timeout() == 60


@pytest.mark.django_db
def test_orca_entries_use_cache_timeout(settings):
    settings.ORCA_SETTINGS = {"CACHE_TIMEOUT": 60}
    clear_cache()
    with mock.patch.object(orca_cache(), "set", wraps=orca_cache().set) as set_:
        string_to_permission("auth.add_group")
    set_.assert_called_once_with(mock.ANY, mock.ANY, timeout=60)
