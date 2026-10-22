# The Graviteron as a unit (v0.4, proposal)

**Definition.** The Graviteron of a claim is the **weight of evidence** that the signed, independent checks give it, in **decibans** (Turing and Good):

    G = 10 · log10(posterior odds) − 10 · log10(prior odds)

Each operator contributes 10 · log10 of its likelihood ratio, from its measured sensitivity and specificity (Dawid-Skene). Code: `graviteron.evidence.unit.reading`.

| Property | Rule | Test |
|---|---|---|
| Zero point | 0 G = no evidence either way | `test_zero_without_evidence` |
| Sign | positive supports, negative contradicts | `test_contradiction_is_negative_and_flagged` |
| Additive | independent operators add | `test_additive_over_independent_operators` |
| Sybil invariant | all keys of one operator count once | `test_keys_of_one_operator_count_once` |
| Dynamic | a check loses weight with a half life unless renewed | `test_decay_with_half_life_and_renewal` |
| No silent evidence | no verdict, or no measured reliability, counts nothing and is noted | `test_no_verdict_and_unknown_operator_count_nothing` |
| Never a bare point | an interval, narrower with more independent operators | `test_interval_contains_value_and_narrows_with_more_operators` |
| Contradiction visible | any signed "false" is flagged and the band reads "contested" | `test_contradiction_is_negative_and_flagged` |

## How people read it

Numbers invite false precision. The reading shows a **verbal band** on Jeffreys' scale for Bayes factors (in decibans), the **number of independent operators**, and a **contradiction flag** that is never averaged away.

| \|G\| in dB | Band |
|---|---|
| below 5 | inconclusive |
| 5 to 10 | substantial |
| 10 to 15 | strong |
| 15 to 20 | very strong |
| 20 and more | decisive |

## Examples (operators with 90 % / 90 % and 80 % / 95 % measured accuracy)

| Situation | G (dB) | 90 % interval | Band |
|---|---|---|---|
| one operator confirms | 9.5 | −0.3 to 22.4 | substantial support |
| three independent operators confirm | 31.1 | 23.5 to 44.0 | decisive support |
| two confirm, one signs "false" | 12.3 | 4.0 to 22.5 | **contested:** strong support |
| three confirm, all checks 60 days old, half life 30 days | 7.8 | −2.0 to 20.6 | substantial support |

## Honest limits

- The interval is **provisional**: it reflects how much independent evidence there is, not yet the uncertainty of the operators' measured accuracy. Next step: carry the Dawid-Skene sample sizes into the interval.
- The bands are a communication scale (Jeffreys), not a decision rule. The Verified Fact decision of the verifier stays separate and does not depend on the Graviteron.
- Calibration on live data (EURAU, CHFAU, the public receipt log) is the next measurement; results will be published with their data, as before.
