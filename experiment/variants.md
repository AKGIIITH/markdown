# Decision experiments

The [comparison ledger](comparisons.md) records three side-by-side comparisons.
The two primary ADR comparisons used matching public inputs.

| Decision | Variant A | Variant B | Measurement |
| --- | --- | --- | --- |
| Requirements format | JSON object | Strict JSON schema | Structural acceptance and the independent requirements gate on Issues 1, 2, and 4 |
| Builder Testing context | Retain the Implementation answer | Provide the patch and public examples | Candidate and clean test outcomes and reported token usage on Issue 3 |
| Design writing evidence | Broad repository excerpts | Focused pinned excerpts | Completion, gate outcome, and reported token usage on Issue 3 |

The recorded Design and Testing comparisons were stage experiments. The
five original GitHub Actions runs and guided PR outcomes are listed in the
[run ledger](../results/runs.md).
