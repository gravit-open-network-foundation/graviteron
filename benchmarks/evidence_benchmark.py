#!/usr/bin/env python3
"""Graviteron v0.2 benchmark: is the measure calibrated, and does it resist Sybil keys?

Part A, simulated, every assumption stated and fixed before the run:
  * 2000 claims; each is true with probability 0.5 (seed 20261013).
  * Six honest operators with hidden accuracies 0.95, 0.90, 0.85, 0.80, 0.70, 0.60.
    Each answers a claim with probability 0.7; 10 % of answers are "no verdict" (None);
    otherwise it is right with its accuracy. One key per honest operator.
  * One Sybil operator answers every claim with True, from K keys (K = 1, 10, 50).
Methods compared on the same data:
  * key_majority  share of True among all keys (what naive counting does)
  * gevp_rule     1 if at least two distinct operators say True and none says False, else 0
  * graviteron_equal       Subjective Logic, every operator trusted equally
  * graviteron_discounted  Subjective Logic, operators discounted by trust 2p - 1 learned by Dawid-Skene
  * graviteron_weighted    Subjective Logic, each verdict carries evidence (2p - 1) / (1 - p) from the
                           accuracy p learned by Dawid-Skene (no labels used)
  * dawid_skene_posterior  the Dawid-Skene posterior itself
Part B, real data: the 3000-claim Grover calibration trace (network confidence vs label).

Writes benchmarks/results/evidence-benchmark.json and .md. Deterministic.
"""

import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from graviteron.evidence import dawid_skene, evidence_from_accuracy, graviteron, report, trust_from_accuracy  # noqa: E402

SEED, N_CLAIMS = 20261013, 2000
HONEST = {"op-a": 0.95, "op-b": 0.90, "op-c": 0.85, "op-d": 0.80, "op-e": 0.70, "op-f": 0.60}
ANSWER_P, NULL_P = 0.7, 0.10
OUT = ROOT / "benchmarks" / "results"
GROVER_MERKLE_ROOT = "370326aa26d4cf7e5c87fa66e9809e6eeb451a29697ee7c9117b60d5599ac25d"


def merkle_root(leaves):
    """Binary SHA-256 Merkle tree over hex leaf hashes; an odd node is paired with itself (as in gravit-grover)."""
    level = [bytes.fromhex(h) for h in leaves]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256(level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return level[0].hex()


def simulate(sybil_keys: int):
    rng = random.Random(f"{SEED}-{sybil_keys}")
    claims = []
    for i in range(N_CLAIMS):
        truth = rng.random() < 0.5
        records = []  # (operator, key, result)
        for op, acc in HONEST.items():
            if rng.random() < ANSWER_P:
                if rng.random() < NULL_P:
                    records.append((op, op, None))
                else:
                    records.append((op, op, truth if rng.random() < acc else (not truth)))
        records += [("op-sybil", f"op-sybil-{k}", True) for k in range(sybil_keys)]
        claims.append({"id": f"c{i:04d}", "truth": truth, "records": records})
    return claims


def operator_verdicts(claim):
    """One verdict per operator: majority of its keys' non-null verdicts (None if none or tied)."""
    by_op = {}
    for op, _, r in claim["records"]:
        by_op.setdefault(op, []).append(r)
    out = {}
    for op, rs in by_op.items():
        votes = [r for r in rs if r is not None]
        t = sum(1 for r in votes if r)
        out[op] = None if not votes or 2 * t == len(votes) else (2 * t > len(votes))
    return out


def run_part_a():
    rows = {}
    for k in (1, 10, 50):
        claims = simulate(k)
        truth = [c["truth"] for c in claims]
        verdicts = {c["id"]: operator_verdicts(c) for c in claims}
        post, params, prior = dawid_skene(verdicts)
        trust = {op: trust_from_accuracy(p["accuracy"]) for op, p in params.items()}
        weight = {op: evidence_from_accuracy(p["accuracy"]) for op, p in params.items()}
        scores = {"key_majority": [], "gevp_rule": [], "graviteron_equal": [], "graviteron_discounted": [],
                  "graviteron_weighted": [], "dawid_skene_posterior": []}
        for c in claims:
            votes = [r for _, _, r in c["records"] if r is not None]
            scores["key_majority"].append(sum(votes) / len(votes) if votes else 0.5)
            ov = verdicts[c["id"]]
            yes = sum(1 for v in ov.values() if v is True)
            no = sum(1 for v in ov.values() if v is False)
            scores["gevp_rule"].append(1.0 if yes >= 2 and no == 0 else 0.0)
            recs = [(op, r) for op, _, r in c["records"]]
            scores["graviteron_equal"].append(graviteron(recs).expected)
            scores["graviteron_discounted"].append(graviteron(recs, reliability=trust).expected)
            scores["graviteron_weighted"].append(graviteron(recs, evidence_weight=weight).expected)
            scores["dawid_skene_posterior"].append(post[c["id"]])
        rows[f"sybil_keys_{k}"] = {
            "methods": {m: {kk: round(v, 4) for kk, v in report(s, truth).items()} for m, s in scores.items()},
            "learned_operator_accuracy": {op: round(p["accuracy"], 3) for op, p in sorted(params.items())},
        }
    return rows


def run_part_b():
    # Copy of gravit-grover experiments/results/theta-calibration.jsonl; its Merkle root must equal the one
    # published in the grover summary and in draft-gravit-gevp-08/09, so anyone can check it is the same trace.
    trace = ROOT / "benchmarks" / "data" / "grover-theta-calibration.jsonl"
    recs = [json.loads(line) for line in trace.read_text().splitlines()]
    root = merkle_root([r["record_hash"] for r in recs])
    if root != GROVER_MERKLE_ROOT:
        raise SystemExit(f"Grover trace Merkle root {root} differs from the published {GROVER_MERKLE_ROOT}")
    # claims labelled "honest" are true claims; the network confidence is its probability that the claim is true
    scores = [r["confidence"] for r in recs]
    truth = [r["label"] == "honest" for r in recs]
    return {"source": "gravit-grover theta-calibration.jsonl (3000 claims, seed 20261011, Merkle root sha256:" + root + ")",
            "network_confidence": {k: round(v, 4) for k, v in report(scores, truth).items()}}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"seed": SEED, "claims": N_CLAIMS, "honest_operators": HONEST, "part_a": run_part_a(), "part_b": run_part_b()}
    (OUT / "evidence-benchmark.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    lines = ["# Graviteron v0.2 benchmark", "", "Lower Brier, log loss and ECE are better; higher AUC is better.", ""]
    for k, row in res["part_a"].items():
        lines += [f"## Part A, {k.replace('_', ' ')}", "", "| Method | Brier | Log loss | ECE | AUC | Accuracy | False accept | True accept |", "|---|---|---|---|---|---|---|---|"]
        for m, r in row["methods"].items():
            lines.append(f"| {m} | {r['brier']} | {r['log_loss']} | {r['ece']} | {r['auc']} | {r['accuracy_at_0.5']} | {r['false_accept_rate']} | {r['true_accept_rate']} |")
        lines += ["", "Learned operator accuracy (true values: a .95, b .90, c .85, d .80, e .70, f .60; Sybil says True always): "
                  + ", ".join(f"{op} {a}" for op, a in row["learned_operator_accuracy"].items()), ""]
    b = res["part_b"]
    lines += ["## Part B, real Grover trace", ""]
    lines += [f"- {b.get('source', b.get('skipped'))}"]
    if "network_confidence" in b:
        r = b["network_confidence"]
        lines += [f"- network confidence: Brier {r['brier']}, log loss {r['log_loss']}, ECE {r['ece']}, AUC {r['auc']}, accuracy {r['accuracy_at_0.5']}"]
    (OUT / "evidence-benchmark.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
