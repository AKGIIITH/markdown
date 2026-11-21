# ADR-013. Pace hosted requests and repair from isolated checks

## Status

Accepted for the demo configuration. Revises the hosted defaults in ADR-009
and ADR-012. The earlier decisions and experimental configurations are retained.

## Context

GPT-OSS 120B handled bounded tasks but the Issue 3 test-writing prompt and
completion reservation exceeded the reported 8,000-token minute quota.
Tool history accumulated successive excerpts. Issue 2 achieved passing
unit tests but failed the changelog check. Issue 3 hit whitespace and spelling
checks after publication. The provider quota is shared by deployed model jobs.

## Decision

Use GPT-OSS 120B for each hosted model role. The transport reserves token
headroom, waits at least 60 seconds between requests within a job, and retries
one transient provider failure. A call counter bounds each model job. Use
LangGraph to keep Builder lookups and Planner clarification bounded. For
the two demo cases, start Design from checked public source and test ranges.

Run the generated tests and source lint inside an isolated container before
freezing the candidate, and supply one bounded repair opportunity with public
diagnostics. Generate the changelog entry from the trusted issue mapping. Use
the tested patch digest in Release. Review still starts fresh on the published
head. The maintainer applies round-one findings and requests the second review
with a PR comment.

## Consequences

Seconds of model latency become minutes of workflow latency. GitHub model
jobs share one concurrency group, so the demo submits the cases serially.
Shorter histories reduce prompt usage and can omit previously inspected detail.
The byte-based budget is a local estimate. Groq can still reject an individual
request or exhaust the daily quota. Docker isolates candidate execution from
runner credentials. Two local replays reach Release preflight. The new
hosted configuration requires a live validation run.
