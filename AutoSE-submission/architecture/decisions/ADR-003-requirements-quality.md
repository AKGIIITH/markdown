# ADR-003 — Automate the requirements-quality gate

## Status

Accepted for the autonomous baseline. Supersedes the maintainer quality check
in ADR-002 for autonomous runs. ADR-002 still describes the early pilot and its
provider and structural checks.

## Context

The Issue #3 pilot required a maintainer to assess requirements after structural
validation. That check caught an unsupported interpretation. Requiring the
same intervention for every issue prevents routine automated handoffs from
Requirements to Design.

## Decision

After structural validation, request a fresh Groq judgment with the issue and
proposed specification. Check that every criterion has one grounding and
testability judgment. A complete positive judgment allows Design to start.
Unsupported or untestable criteria return to Requirements within the agreed
retry budget. A material unresolved product question pauses for maintainer
input. An incomplete or malformed judgment fails the quality gate.

The maintainer selected this baseline policy. The original pilot evidence and
maintainer decisions remain part of its own run history.

## Consequences

Each live quality check adds one model call. The model can miss unsupported
criteria or flag a reasonable interpretation as ambiguous. Record per-criterion
judgments, provider usage and routing outcomes so later evaluation can compare
the gate's judgments with observed results.
