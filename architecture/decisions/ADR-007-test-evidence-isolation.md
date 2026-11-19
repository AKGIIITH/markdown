# ADR-007 — Separate public gates from private evaluation

## Status

Accepted for the baseline.

## Context

The Builder needs executable acceptance feedback. Private tests measure
whether the resulting patch generalizes beyond that feedback. Test code from
the model must run without model or push credentials.

## Decision

Execute the same public tests against the clean and candidate applications.
Verify that the candidate passes the public tests and full suite and that the
clean run detects the reported missing behavior. Run private tests separately
after freezing the revision. The hosted test job receives the patch and
public tests with read-only repository permissions. Private test files and
results stay outside model inputs.

## Consequences

The public gate records evidence the Builder can use for repair. Private
evaluation can detect missed behavior without influencing the agents.
Reports must distinguish an expected clean regression from a collection,
dependency, or runner failure.
