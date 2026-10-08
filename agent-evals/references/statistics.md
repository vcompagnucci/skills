# Statistics

Every formula the skill uses, each with a check value. Copy the formula, run its check value through your code, and trust the code only when they match. Pass is the positive class throughout.

## Pick the unit and the method

- **The unit is the case, never the run.** Average each case's runs, or take its pass^k outcome, then compute every interval over cases. Pooling 15 runs per case as independent draws inflates n 15-fold and makes the interval far too narrow. Every n on this page counts independent cases or conversations, never runs.
- **Variants of one scenario are one cluster, not independent cases.** Paraphrases, translations, and the same case with a different user pass and fail together. Report the scenario count next to the case count, and size with the effective n for clustered cases: n / (1 + (m - 1)ρ), for m variants per scenario with correlation ρ. Check: 200 cases that are 40 scenarios × 5 variants with ρ = 1 give 40. Naive standard errors on clustered evals came out 1.1 to 3.05 times too small.
- **Under a few hundred cases, never use a normal-approximation (mean ± 1.96 SE) or plain percentile-bootstrap interval for a rate or a difference.** At 100 cases a nominal 95% normal interval covered only 92.5%, and clustering didn't fix it. Use Wilson for one rate and the exact paired test for two versions, and keep one variant per scenario in either. The corrected production rate and the difference in J keep their bootstrap. With thousands of cases, the standard error over per-case means, clustered on scenario, is fine.

## One rate

- **Wilson interval.** With x of n, p = x/n and z = 1.96: center = (p + z²/2n) / (1 + z²/n), half-width = z / (1 + z²/n) × √(p(1-p)/n + z²/4n²). Check: 16 of 20 gives 0.584 to 0.919.
- **Size the sample for a ship decision before drawing it.** The ship rule is in testing.md. If the true failure rate is 3% against a 5% limit, 200 samples prove it 15% of the time and 800 about 77%; at exactly 3% observed, 460 suffice. Halving the margin takes four times the samples.
- **Zero failures seen: size the sample before agreeing to a zero-tolerance gate.** With 0 failures in n independent conversations, the Wilson upper bound is 3.84/(n + 3.84), about 4/n. Check: 0 of 200 gives 0.0188, and showing under 0.1% takes about 3,840 clean conversations.

## Runs of one case

- **Estimate pass@k and pass^k from n runs, never by rerunning k times.** With c passes in n runs: pass@k = 1 - C(n-c, k) / C(n, k), and pass^k = C(c, k) / C(n, k). Check: 6 of 8 gives pass@2 = 0.964 and pass^4 = 0.214.
- **The noise band ±1/√(cases × runs) answers one question: is this change bigger than rerunning the same cases?** Check: 25 cases × 2 runs moves about ±14 points by chance. It's the special case where all variance sits within cases, so it's too narrow for whether a gain holds on new traffic whenever per-case pass rates spread (some cases always pass, some always fail). Answer that one with an interval over cases.
- **Add cases, not runs, once rerun noise is small.** Runs shrink only the within-case variance. With binary scores and uniform case difficulty, K runs scale total variance by (1 + 2/K)/3. Check: K = 2 cuts it by 1/3, K = 4 by 1/2, K = 6 by 5/9, and no K cuts more than 2/3. This sizes estimates. A case that gates a release still runs 15 times (rule 6).
- **Never lower the agent's temperature to cut eval noise.** It moves variance into the between-case term or biases the score: rounding uniform case difficulty to temperature 0 tripled the irreducible variance, from 1/12 to 1/4.

## Size a comparison before running it

- **Cases needed for the smallest difference you'd act on:** n = (z_α/2 + z_β)² × (ω² + σ_A²/K_A + σ_B²/K_B) / δ². ω² = Var(x_A) + Var(x_B) - 2Cov(x_A, x_B) is the between-case variance of the difference, σ² the mean within-case variance, K the runs per case, δ the difference. Check: z_α/2 = 1.96, z_β = 0.8416 (power 0.80), ω² = 1/9, σ² = 0, δ = 0.03 gives about 969 cases.
- **Smallest difference your cases can detect:** δ = (z_α/2 + z_β) × √((ω² + σ_A²/K_A + σ_B²/K_B) / n). Check: the same z values, n = 198, ω² = 1/9, and σ² = 1/6 give 0.1327 at K = 1 and 0.0757 at K = 10. A gain smaller than δ is invisible to the eval. K here sizes the estimate; a gating case still runs 15 times (rule 6).

## Compare two versions

- **Decide with the exact one-sided paired test, never two separate intervals.** On the same cases, count b (baseline passed, candidate failed) and c (the reverse); ties carry no information. p = P(X ≥ b) for X ~ Binomial(b + c, 0.5). Check: b = 1,241 and c = 1,042 give 1.69e-05; b = 163 and c = 168 give 0.629. Report wins, losses, and ties beside it. The same test compares two judge versions on the same labeled items.
- **Across several suites, flag a regression if any of three tests rejects,** which bounds false alarms at 3α. Pooled: the paired test on the summed b and c. Fisher: χ² = -2 Σ ln p_i over the T suites' paired-test p-values, with 2T degrees of freedom. Max drop: the largest z_i = (b_i / (b_i + c_i) - 0.5) / √(0.25 / (b_i + c_i)), with p the share of simulated maxima at or above it, each simulation drawing every b_i from Binomial(b_i + c_i, 0.5).
- **Check the three before trusting them.** Six suites with (b, c) of (250, 234), (25, 25), (23, 23), (448, 347), (479, 393), and (16, 20) give pooled 1.69e-05, Fisher 4.44e-04, and max drop about 9e-04.
- **Drop cases that never flip from comparison batches, never from CI.** They carry no information about the difference: 5,604 of 12,032 cases never flipped across 10 noisy runs, and removing them nearly halved the set while keeping most flips.
- **Inside the noise, declare no winner.** When the paired test doesn't reject, decide on the code-verified outcome or on more cases. A gate that ranked 25 agents at rank correlation 0.94 still promoted the worse one on 31% of near-equal pairs, a four-judge average gave the same 31%, and abstaining halved the error to 14.8%. Re-audit the gate whenever its configuration changes.
- **Count every comparison behind one decision and report the count.** 10 variants at α = 0.05 give about a 40% chance that one clears the bar by luck (1 - 0.95^10 ≈ 0.40). When one decision reads many metrics, modes, languages, or variants, correct with Benjamini-Hochberg from a tested statistics library, and confirm only the chosen variant on cases it never touched.
- **Reconcile attempted, completed, and errored runs per arm before reading any average.** Rerun an arm whose completed count fell below its peers: one six-model comparison averaged an arm over 43 survivors after 197 of 240 rows errored. Then check the conclusion survives dropping the single most favorable category.

## Judge agreement

- **Difference in J between two versions.** Each version has its own expert-labeled sample, so compute J = TPR + TNR - 1 per side and report J_A - J_B. Check: A passing 46 of 50 human Passes and failing 42 of 50 Fails (J = 0.76) against B at 40 of 50 and 44 of 50 (J = 0.68) gives 0.08.
- **Its interval: seeded percentile bootstrap, 95%, at least 2,000 draws,** each draw resampling both sides' Passes and Fails separately, with replacement, at their original counts. When it excludes zero, follow judges.md.

## Corrected production rate

- **Rogan-Gladen.** With TPR and TNR from the frozen judge's test split (never dev, which is optimistic) and p_obs the share the judge passed in a random sample: true pass rate = (p_obs + TNR - 1) / (TPR + TNR - 1). The failure rate is 1 minus that. Clip to [0, 1]. Check: TPR 0.92, TNR 0.88, p_obs 0.80 gives 0.85. Its variance grows as 1/(TPR + TNR - 1)², so near zero the correction is meaningless: fix the judge instead.
- **Keep Rogan-Gladen while the judge's labels are balanced or enriched.** It stays unbiased when the labeled set's pass rate differs from production's. Prediction-powered estimators (PPI++) give intervals about 3 times narrower but go biased under that shift, so use them only when the human labels are a random subsample of the monitored traffic. When the judge errs differently by stratum (language, reply length), estimate TPR and TNR and correct each stratum separately.
- **Interval: seeded percentile bootstrap, 95%, at least 2,000 draws.** Each draw resamples the monitored verdicts and the held-out (label, prediction) pairs independently, with replacement, at their original sizes. It recomputes TPR, TNR, and the corrected rate, discards the draw if a class is missing or TPR + TNR - 1 is zero, and clamps to [0, 1]. Resampling only the test pairs ignores the sampling error of the monitored period and makes the interval too narrow.
- **The corrected rate must beat direct labeling.** For a judge with TPR = TNR = q calibrated on balanced labels, it's tighter than an expert labeling the same number of random traces only when θ(1 - θ) ≥ 2q(1 - q), where θ is the true pass rate. Check: q = 0.8 never qualifies, q = 0.9 only for θ between 0.235 and 0.765, q = 0.95 between 0.106 and 0.894. Outside that range, label a random sample directly and use Wilson.
- **If the calibration labels are a random sample of traffic instead,** the condition is θ(1 - θ) ≥ q(1 - q) / (2q - 1)². Check: q = 0.9 qualifies for θ between 0.169 and 0.831, q = 0.95 between 0.063 and 0.937.

## Break-even, attack success, and abstention

- **Break-even accuracy = C / (V + C),** where V is the value of a resolved case and C the expected cost of a failure, the sum over failure kinds of share × cost. The failure-rate requirement is 1 minus it. Check: V = $20, unneeded escalations at $40 (95% of failures), and lost customers at $1,000 (5%) give C = $88, break-even 81.5%, and a requirement of 18.5%.
- **Attack success at k tries.** 1 - (1 - p)^k holds only for independent attempts (check: p = 0.01, k = 392 gives 0.98). Adaptive attempts aren't independent, so report the measured share (red-team.md).
- **Abstention score against a confidence target t:** correct +1, abstained 0, wrong -t/(1-t). Check: t = 0.5 gives a wrong answer -1, t = 0.75 gives -3, t = 0.9 gives -9.
