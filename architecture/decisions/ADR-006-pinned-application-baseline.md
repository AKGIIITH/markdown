# ADR-006 — Pin the application baseline independently of the harness

## Status

Accepted for the baseline.

## Context

The harness changes while the defect measurements need a reproducible
starting point. Issue #2 deliberately seeds a regression and uses a different
base from the other four issues.

## Decision

Map Issues #1, #3, #4, and #5 to application commit `2c96e36` and PR base
`main`. Map Issue #2 to `1e2b7f2` and `a3/bug02-seed`. Read, build,
and test the pinned application. Record the harness commit separately.
Before publishing, check that the fork's base still contains the application
revision and matches the pinned application and CI inputs.

## Consequences

Application-only comparisons stay reproducible as the workflow changes.
If the base branch changes application, suite, or CI inputs, release stops
until the maintainer resolves the mismatch.
