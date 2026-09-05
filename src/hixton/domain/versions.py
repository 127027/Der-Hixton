"""Explicit immutable strategy definitions; runtime activation is intentionally separate."""

from __future__ import annotations

from dataclasses import dataclass

from hixton.constants import (
    HIXTON_SPEC_VERSION,
    HIXTON_V2_RESEARCH_VERSION,
    HIXTON_V3_SLOT_VERSION,
)
from hixton.domain.allocation import ONE_PER_SYMBOL, RANKED_REPEAT
from hixton.domain.models import StrategyParameters, StrategySemantics


@dataclass(frozen=True, slots=True)
class StrategyDefinition:
    key: str
    backtest_version: str
    version: str
    reference: str
    semantics: StrategySemantics
    parameters: StrategyParameters
    paper_approved: bool
    slot_allocation: str


V1_STRATEGY = StrategyDefinition(
    key="v1",
    backtest_version="v1",
    version=HIXTON_SPEC_VERSION,
    reference="DMS/03_STRATEGIE_HIXTON.md",
    semantics=StrategySemantics.DMS_V1,
    parameters=StrategyParameters(),
    paper_approved=False,
    slot_allocation=ONE_PER_SYMBOL,
)

V2_RESEARCH_STRATEGY = StrategyDefinition(
    key="v2",
    backtest_version="v2",
    version=HIXTON_V2_RESEARCH_VERSION,
    reference="strategy/pine/Der_Hixton_Indikator_v6.pine",
    semantics=StrategySemantics.PINE_V6,
    parameters=StrategyParameters(
        vidya_length=6,
        momentum_length=20,
        smoothing_length=8,
        atr_length=60,
        band_multiplier=3.8,
        warmup_bars=400,
    ),
    paper_approved=True,
    slot_allocation=ONE_PER_SYMBOL,
)

V3_SLOT_STRATEGY = StrategyDefinition(
    key="v3",
    backtest_version="v3",
    version=HIXTON_V3_SLOT_VERSION,
    reference="DMS/03_STRATEGIE_HIXTON.md",
    semantics=StrategySemantics.PINE_V6,
    parameters=V2_RESEARCH_STRATEGY.parameters,
    paper_approved=False,
    slot_allocation=RANKED_REPEAT,
)

STRATEGY_DEFINITIONS = {
    V1_STRATEGY.key: V1_STRATEGY,
    V2_RESEARCH_STRATEGY.key: V2_RESEARCH_STRATEGY,
    V3_SLOT_STRATEGY.key: V3_SLOT_STRATEGY,
}


def strategy_definition(key: str) -> StrategyDefinition:
    try:
        return STRATEGY_DEFINITIONS[key.lower()]
    except KeyError as error:
        raise ValueError(f"unsupported strategy version: {key}") from error
