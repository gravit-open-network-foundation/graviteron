#!/usr/bin/env python3
"""CHFAU on Ethereum, 30 days: supply, mints, burns, transfers, concentration. Deterministic.

Reads only data/transfers.json (checked against data/SHA256SUMS). Writes results.md and results.json.
"""
import collections
import hashlib
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ZERO = "0x" + "0" * 40


def main():
    data = HERE / "data"
    for line in (data / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        if hashlib.sha256((data / name).read_bytes()).hexdigest() != digest:
            raise SystemExit(f"{name} does not match SHA256SUMS")
    d = json.loads((data / "transfers.json").read_text())
    rows = d["transfers"]
    mints = [r for r in rows if r["from"] == ZERO]
    burns = [r for r in rows if r["to"] == ZERO]
    moves = [r for r in rows if ZERO not in (r["from"], r["to"])]
    s = lambda rs: round(sum(r["amount"] for r in rs), 2)  # noqa: E731
    vol = collections.Counter()
    for r in moves:
        vol[r["from"]] += r["amount"]
        vol[r["to"]] += r["amount"]
    total = sum(vol.values())
    per_day = collections.Counter(r["time"][:10] for r in moves)
    res = {
        "window": d["window"], "source": d["source"], "supply_at_fetch": d["fetched_total_supply"],
        "holders_at_fetch": int(d["fetched_counters"]["token_holders_count"]),
        "transfers": len(rows), "minted": s(mints), "mints": len(mints), "burned": s(burns), "burns": len(burns),
        "net_issuance": round(s(mints) - s(burns), 2), "moved_between_holders": s(moves), "moves": len(moves),
        "addresses_moving": len({r["from"] for r in moves} | {r["to"] for r in moves}),
        "median_moves_per_day": statistics.median(per_day.values()),
        "top5_share_of_volume_pct": [round(v / total * 100, 1) for _, v in vol.most_common(5)],
    }
    (HERE / "results.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    t5 = res["top5_share_of_volume_pct"]
    md = f"""# CHFAU on Ethereum: 30 days on chain ({res['window'][0][:10]} to {res['window'][1][:10]})

Source: {res['source']} (public explorer). Supply at fetch {res['supply_at_fetch']:,.2f} CHFAU, {res['holders_at_fetch']:,} holders.

| | CHFAU | Count |
|---|---|---|
| Minted | {res['minted']:,.0f} | {res['mints']} |
| Burned (redeemed) | {res['burned']:,.0f} | {res['burns']} |
| Net issuance | {res['net_issuance']:,.0f} | |
| Moved between holders | {res['moved_between_holders']:,.0f} | {res['moves']} transfers, {res['addresses_moving']:,} addresses |

Median {res['median_moves_per_day']} transfers between holders per day. The five most active addresses take
{t5[0]} %, {t5[1]} %, {t5[2]} %, {t5[3]} % and {t5[4]} % of the volume sent and received; none carries a public label.
"""
    (HERE / "results.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
