from __future__ import annotations

import pytest

from hixton.domain.allocation import ONE_PER_SYMBOL, RANKED_REPEAT, allocate_entry_slots


def test_one_per_symbol_spreads_three_slots_across_ranked_candidates() -> None:
    assert allocate_entry_slots(
        ["SOLUSDT", "BTCUSDT", "BNBUSDT"],
        free_slots=3,
        policy=ONE_PER_SYMBOL,
    ) == {"SOLUSDT": 1, "BTCUSDT": 1, "BNBUSDT": 1}


def test_ranked_repeat_uses_all_slots_and_matches_owner_examples() -> None:
    assert allocate_entry_slots(
        ["BTCUSDT"], free_slots=3, policy=RANKED_REPEAT
    ) == {"BTCUSDT": 3}
    assert allocate_entry_slots(
        ["SOLUSDT", "BNBUSDT"], free_slots=3, policy=RANKED_REPEAT
    ) == {"SOLUSDT": 2, "BNBUSDT": 1}


def test_allocation_rejects_invalid_policy_or_negative_capacity() -> None:
    with pytest.raises(ValueError, match="unsupported"):
        allocate_entry_slots(["BTCUSDT"], free_slots=1, policy="unknown")
    with pytest.raises(ValueError, match="negative"):
        allocate_entry_slots(["BTCUSDT"], free_slots=-1, policy=RANKED_REPEAT)
