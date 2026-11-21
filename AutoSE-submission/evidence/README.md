# How to read the evidence

Each issue folder holds the specification, design, production patch, final patch including public tests and changelog, test source, local test report, PR record, CI matrix, hosted suite receipt, reviewer excerpts and verdict. The saved pr.md is the publication-time snapshot; ci.json and github.json contain the later result. Paths in original receipts refer to the machines that produced them. The exact SHA and review URL are portable identifiers.

model-calls.csv lists individual provider attempts from the saved issue-triggered handoffs, their focused continuations, the available independent review attempts and the final hosted reviews. Checkpoint names start with a UTC timestamp. An empty usage cell means no usage was reported. A pre-dispatch prompt rejection never reached Groq, so it has no provider row. The ledger does not claim to inventory every historical pilot, billing event or operator interaction. Earlier experiments have separate batch totals in results/runs.md.

## Issue 2 call path

1. The proposal, quality audit and design writer each returned text. Design correctly located slugify. The Builder searched for the separator and read the extension configuration. A third request exceeded the local prompt estimate and stopped before dispatch.
2. The focused submission replay kept the editable source and latest lookup. Groq returned submit_edits. Only the two lines overriding the tilde were removed. Saved guided tests supplied the Testing artifact; release and CI used no model calls.
3. A local fresh review and earlier hosted inspection attempts are retained in the call ledger. The original hosted inspection could stop on a rejected tool request after running its suite. The replacement writer read verified source excerpts directly. The final hosted review used 2,522 tokens and the bot posted on the same SHA.

## Issue 3 call path

1. Proposal → quality audit → revised proposal → second audit. Both audits listed excluded cases. An auditor-only replay still paused. Replaying proposal and audit with explicit scope guidance passed.
2. Design → implementation submission → public test lookup → rejected tool call. A separate text call resumed test writing on the existing implementation. Compilation had missed the boolean conversion caused by the None default. The runtime tests caught it.
3. The repair call proposed a text default against the failed candidate. Composing its exact edit with the earlier edits reproduced a compiling patch on the original pin. A fresh test-writing call used the repaired implementation. The functional suite passed. CI later reported W292, so the harness added the missing final newline before freezing test source.
4. Earlier fresh reviewers used lookup calls. One requested an unavailable local runner; others hit HTTP 400 during inspection. The final hosted version ran the suite in its isolated container and supplied exact source around the production hunks. The final writer used 3,345 tokens. Release, CI, GitHub posting and private evaluation were deterministic jobs with no model calls.

See experiment/issue-3-sdk-trace.md and experiment/issue-3-120b.md for earlier attempts. Their stated statuses refer to those attempts. The final github.json files identify the successful posted reviews.
