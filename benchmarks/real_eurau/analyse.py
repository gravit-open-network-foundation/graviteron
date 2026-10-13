#!/usr/bin/env python3
"""EURAU venue study on real data: how well do simple aggregators and Graviteron price EURAU?

Data: the committed snapshot in data/ (see fetch.py and data/SHA256SUMS), 30 days to 13 Oct 2026.
Reference: the Chainlink EUR/USD round in force at the end of each hour; EURAU is an e-money token
redeemable at par, so its fair USD price is the EUR/USD rate. The ECB daily rate is a second,
independent check of the reference itself.

A venue gives evidence only in hours in which it traded; a price shown without trades is stale.
Verdict of a venue in an hour: its closing price is within TOL of the reference (True) or not (False);
no trade: no verdict (None).

Estimators of the EURAU price in each hour with at least one trade, compared with the reference:
  last_price_mean    mean of every venue's last traded price, however old (what a naive aggregator does)
  last_price_median  median of the same
  fresh_mean         mean over venues that traded in this hour
  graviteron         weighted mean over venues that traded in this hour, weights = evidence units from
                     each venue's accuracy measured on the first 15 days only (held out: scored on days 16-30)
Writes results.json and results.md next to this file. Deterministic.
"""

import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "src"))
from graviteron.evidence.measure import evidence_from_accuracy, graviteron  # noqa: E402

TOL = 0.0025  # 25 basis points
DATA = HERE / "data"


def load():
    for line in (DATA / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        if hashlib.sha256((DATA / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"{name} does not match SHA256SUMS")
    j = lambda n: json.loads((DATA / n).read_text())  # noqa: E731
    return j("venues.json"), j("chainlink_eur_usd.json")["rounds"], j("ecb_eur_usd.json"), j("meta.json")


def bps(p, ref):
    return (p / ref - 1.0) * 1e4


def main():
    venues, rounds, ecb, meta = load()
    from datetime import datetime
    start = int(datetime.fromisoformat(meta["start"]).timestamp())
    end = int(datetime.fromisoformat(meta["end"]).timestamp())
    hours = list(range(start, end, 3600))
    mid = start + 15 * 86400

    def ref_at(t):  # Chainlink answer in force at time t
        r = [x for x in rounds if x["updated_at"] <= t]
        return r[-1]["answer"] if r else None

    # 1. the reference itself against the ECB
    ecb_dev = []
    for day, rates in sorted(ecb.get("rates", {}).items()):
        t = int(datetime.fromisoformat(day + "T14:15:00+00:00").timestamp())  # ECB fixes about 14:15 UTC
        if start <= t < end and ref_at(t):
            ecb_dev.append(abs(bps(ref_at(t), rates["USD"])))

    # 2. venue observations
    names = sorted(venues)
    traded = {v: {r[0]: r[4] for r in venues[v]["ohlcv_hour_usd"]} for v in names}  # hour -> close

    def verdict(v, h):
        p = traded[v].get(h)
        return None if p is None else abs(p / ref_at(h + 3599) - 1.0) <= TOL

    venue_stats, acc_train = {}, {}
    for v in names:
        devs = [bps(p, ref_at(h + 3599)) for h, p in traded[v].items()]
        tr = [verdict(v, h) for h in hours if h < mid and verdict(v, h) is not None]
        acc_train[v] = sum(tr) / len(tr) if tr else 0.5
        venue_stats[v] = {"hours_traded": len(devs), "share_of_hours_traded": round(len(devs) / len(hours), 3),
                          "median_deviation_bps": round(statistics.median(devs), 1) if devs else None,
                          "share_within_25bps": round(sum(1 for d in devs if abs(d) <= TOL * 1e4) / len(devs), 3) if devs else None,
                          "accuracy_days_1_15": round(acc_train[v], 3) if tr else None}
    weight = {v: evidence_from_accuracy(acc_train[v]) for v in names}

    # 3. estimators, scored on days 16-30
    errors = {k: [] for k in ("last_price_mean", "last_price_median", "fresh_mean", "graviteron")}
    g_scores, last = [], {}
    for h in hours:
        for v in names:
            if h in traded[v]:
                last[v] = traded[v][h]
        fresh = {v: traded[v][h] for v in names if h in traded[v]}
        if h < mid or not fresh:
            continue
        ref = ref_at(h + 3599)
        lp = list(last.values())
        errors["last_price_mean"].append(abs(bps(statistics.mean(lp), ref)))
        errors["last_price_median"].append(abs(bps(statistics.median(lp), ref)))
        errors["fresh_mean"].append(abs(bps(statistics.mean(fresh.values()), ref)))
        ws = {v: weight[v] for v in fresh}
        if sum(ws.values()) > 0:
            est = sum(ws[v] * fresh[v] for v in fresh) / sum(ws.values())
        else:
            est = statistics.mean(fresh.values())
        errors["graviteron"].append(abs(bps(est, ref)))
        g = graviteron([(v, verdict(v, h)) for v in fresh], evidence_weight=weight)
        g_scores.append((round(g.expected, 4), round(g.u, 4)))

    def summ(e):
        e = sorted(e)
        return {"hours": len(e), "mean_abs_error_bps": round(statistics.mean(e), 1),
                "p95_abs_error_bps": round(e[int(0.95 * (len(e) - 1))], 1),
                "share_of_hours_off_by_more_than_25bps": round(sum(1 for x in e if x > TOL * 1e4) / len(e), 3)}

    res = {
        "window": [meta["start"], meta["end"]], "tolerance_bps": TOL * 1e4,
        "reference_vs_ecb": {"days": len(ecb_dev), "mean_abs_bps": round(statistics.mean(ecb_dev), 1),
                             "max_abs_bps": round(max(ecb_dev), 1)} if ecb_dev else None,
        "venues": venue_stats,
        "evidence_units_per_verdict": {v: round(w, 3) for v, w in weight.items()},
        "estimators_days_16_30": {k: summ(e) for k, e in errors.items()},
        "graviteron_peg_opinion_days_16_30": {
            "hours": len(g_scores),
            "share_expected_at_least_0.5": round(sum(1 for e, _ in g_scores if e >= 0.5) / len(g_scores), 3),
            "median_expected": statistics.median(e for e, _ in g_scores),
            "median_uncertainty": statistics.median(u for _, u in g_scores)},
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    L = [f"# EURAU venue study (real data, {meta['start'][:10]} to {meta['end'][:10]})", "",
         f"Reference: Chainlink EUR/USD. Against the ECB daily rate it differs on average by "
         f"{res['reference_vs_ecb']['mean_abs_bps']} bps (max {res['reference_vs_ecb']['max_abs_bps']} bps, "
         f"{res['reference_vs_ecb']['days']} days).", "",
         "## Venues", "", "| Venue | Hours traded (of 720) | Median deviation, bps | Within 25 bps | Accuracy, days 1 to 15 |",
         "|---|---|---|---|---|"]
    for v, s in venue_stats.items():
        L.append(f"| {v} | {s['hours_traded']} | {s['median_deviation_bps']} | {s['share_within_25bps']} | {s['accuracy_days_1_15']} |")
    L += ["", "## Pricing EURAU, days 16 to 30 (held out)", "",
          "| Estimator | Hours | Mean error, bps | 95th percentile, bps | Hours off by more than 25 bps |", "|---|---|---|---|---|"]
    for k, s in res["estimators_days_16_30"].items():
        L.append(f"| {k} | {s['hours']} | {s['mean_abs_error_bps']} | {s['p95_abs_error_bps']} | {s['share_of_hours_off_by_more_than_25bps']} |")
    gp = res["graviteron_peg_opinion_days_16_30"]
    L += ["", f"Graviteron opinion that EURAU trades at par: expected at least 0.5 in {gp['share_expected_at_least_0.5']} "
          f"of {gp['hours']} hours; median expected {gp['median_expected']}, median uncertainty {gp['median_uncertainty']}."]
    (HERE / "results.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
