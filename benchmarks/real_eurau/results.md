# EURAU venue study (real data, 2026-09-13 to 2026-10-13)

Reference: Chainlink EUR/USD. Against the ECB daily rate it differs on average by 9.9 bps (max 43.7 bps, 22 days).

## Venues

| Venue | Hours traded (of 720) | Median deviation, bps | Within 25 bps | Accuracy, days 1 to 15 |
|---|---|---|---|---|
| base-EURAU/EURC0.01% | 16 | 1.3 | 0.938 | 0.917 |
| base-EURAU/USDC0.05% | 205 | -17.2 | 0.41 | 0.401 |
| raydium-sol-EURAU/USDC | 69 | 1.4 | 0.58 | 0.636 |
| raydium-sol-EURAU/USDT | 0 | None | None | None |
| uniswap-eth-EURAU/USDC | 90 | -0.5 | 0.956 | 0.967 |
| uniswap-eth-EURAU/USDT | 0 | None | None | None |

## Pricing EURAU, days 16 to 30 (held out)

| Estimator | Hours | Mean error, bps | 95th percentile, bps | Hours off by more than 25 bps |
|---|---|---|---|---|
| last_price_mean | 56 | 36.6 | 106.4 | 0.375 |
| last_price_median | 56 | 46.3 | 128.6 | 0.375 |
| fresh_mean | 56 | 21.3 | 56.7 | 0.304 |
| graviteron | 56 | 19.8 | 56.7 | 0.268 |

Graviteron opinion that EURAU trades at par: expected at least 0.5 in 0.929 of 56 hours; median expected 0.9299, median uncertainty 0.0667.
