"""Graviteron v0.2: a measure of trust computed from signed evidence (Subjective Logic),
with operator reliability learned from data (Dawid-Skene) and checked by calibration."""

from .calibration import auc, brier, ece, log_loss, reliability_bins, report
from .measure import (
    VERSION,
    evidence_from_accuracy,
    graviteron,
    graviteron_v3,
    operator_verdicts,
    record_opinion,
    trust_from_accuracy,
)
from .opinion import Opinion, averaging_fusion, cumulative_fusion, discount, from_evidence
from .reliability import dawid_skene
from .unit import GraviteronReading, band, reading

__all__ = [
    "VERSION",
    "Opinion",
    "from_evidence",
    "cumulative_fusion",
    "averaging_fusion",
    "discount",
    "graviteron",
    "graviteron_v3",
    "operator_verdicts",
    "record_opinion",
    "trust_from_accuracy",
    "evidence_from_accuracy",
    "dawid_skene",
    "reading",
    "band",
    "GraviteronReading",
    "brier",
    "log_loss",
    "ece",
    "auc",
    "reliability_bins",
    "report",
]
