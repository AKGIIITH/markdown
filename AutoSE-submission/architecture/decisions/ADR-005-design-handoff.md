# ADR-005 — Separate Design evidence lookup from handoff writing

## Status

Accepted for the baseline. Extends the pinned-source policy in ADR-004.

## Context

In two live Issue #3 attempts the Planner tried to call a lookup tool in its
final writing turn. Groq rejected both requests. In the second attempt the
Planner inspected application source but only listed public test paths. An
explicit reminder and a larger final completion cap did not resolve the failure.

## Decision

Reserve one model call for writing. Use the remaining calls to gather source
and public-test excerpts. Stop lookup as soon as both categories are present.
If either category is missing when the lookup budget ends, stop at Design and
record which category is missing. Start writing in a fresh conversation with
the issue, accepted requirements, architecture and successful excerpts. Supply
no tool definitions or tool-response history to the writing call.

## Consequences

The logs distinguish evidence collection from writing failures. A broad listing
cannot count as a public-test read. The Planner may stop after collecting a
small amount of evidence, so a successful structural gate still needs
evaluation against actual implementation and test results.
