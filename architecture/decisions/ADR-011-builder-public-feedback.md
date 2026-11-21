# ADR-011 — Return public failures to Builder and reuse compiled edits

## Status

Experimental local stage handoffs. The live repair and offline test-only
restart have been exercised.

## Context

The Issue #3 design passed structural validation with a defective default.
Builder followed the design, and compilation passed. The clean project
suite passed, while four public tests errored on the candidate. The actual
configuration API rejected the requested class strings. A new Builder
attempt corrected the default using the public runner output. Its separate
test-generation response exhausted the existing completion allowance.

## Decision

Allow a Builder attempt to consume a failed public-test receipt for the same
issue and application revision. Supply the previous production patch and
bounded public runner results. Keep the accepted criteria intact. Preserve
the prior attempt. For a test-generation failure, let Builder reconstruct a
previously compiled patch from the original response and pinned source.
Verify the reconstructed diff byte for byte before asking for tests again.

## Consequences

A product error can reach Builder in a reproducible handoff. A test-only
restart spends no provider tokens on Implementation. The local operator
initiates these handoffs. Hosted retry wiring and its budget policy remain
separate work.
