# EURAU venue study: Graviteron on real market data

First test of Graviteron on real data, from public sources only, 30 days to 13 October 2026.

* `fetch.py` downloaded the data once: hourly prices of every EURAU pool found on GeckoTerminal
  (Ethereum, Base, Solana), every round of the Chainlink EUR/USD feed on Ethereum, and the ECB daily
  EUR/USD rate. The snapshot is in `data/`, with `SHA256SUMS`.
* `analyse.py` uses only the snapshot and is deterministic: `python benchmarks/real_eurau/analyse.py`.
* Results: [`results.md`](results.md), [`results.json`](results.json).

## What it shows

* **The market is thin.** Of six pools, two never traded in 30 days, although data sites show a
  price for them (stale quotes 1.3 to 1.6 % above par were visible on 13 October). The busiest pool
  traded in 205 of 720 hours.
* **Venues differ in reliability, and Graviteron measures it.** Measured on the first 15 days, the share
  of a venue's trades within 25 basis points of the reference ranges from 0.97 (Uniswap on Ethereum)
  to 0.40 (the EURAU/USDC pool on Base, which traded at a median discount of 17 basis points).
* **Pricing.** On the held-out days 16 to 30, a reliability-weighted price (weights measured on days 1
  to 15) is off by 19.8 bps on average, against 36.6 bps for the mean of every venue's last price.
  Against a plain mean of the venues that traded in the same hour (21.3 bps) the gain is small, and the
  sample is only 56 hours: this is a first measurement, not a proof.
* **The reference is measured too.** Chainlink EUR/USD differs from the ECB daily rate by 9.9 bps on
  average (max 43.7 bps).

## Limits

* EURAU is redeemable at par, so its fair price is taken as the EUR/USD rate; we do not observe
  redemptions.
* Hourly closing prices from one data provider; trades inside an hour are not seen.
* CHFAU, SEKAU and USDAU had no pool on GeckoTerminal in this window, so the study covers EURAU only.
