# Monitor production

- **Cheap checks and one auditor judge on every ticket,** and the same checks on human agents' tickets, so you compare the agent with the team and not with perfection.
- **Estimate the failure rate only from a random sample.** Correct it for the judge's measured error (Rogan-Gladen) and report a bootstrap interval. Risk groups (tickets with writes, policy lookups, long conversations) are for inspection, never for the rate: they're chosen because they fail more.
- **Fix the alert threshold before looking at results.** Alert when the lower bound of the interval crosses it, not the point estimate. A crossing starts a new round of error analysis and adds CI cases.
- **Pick risk groups from trace evidence** (a tool wrote something, a policy was looked up), not from what the reply says.
- **Reject a monitoring period whose traces came from a different model** than the one the judge was validated on.
- **Measure resolution, don't assume it.** Count customers who come back on the same issue within 7 days. A conversation that ends without a handoff isn't resolved: one team that believed it resolved 40% found 20% on full review, the rest were abandonments.
- **Evaluate the monitors too.** A monitor judge (for frustration, for policy breaks) needs the same validation as any judge, with its rationale shown on every flag.
- **Re-run error analysis** every 2 to 4 weeks on 100+ fresh traces and after every incident. New failure modes appear as customers, products, and models change.
