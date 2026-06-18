from __future__ import annotations

from local_search import config


def test_search_contract_versions_remain_code_owned():
    assert config.SCHEMA_VERSION == 1
    assert config.RETRIEVAL_VERSION == 1
