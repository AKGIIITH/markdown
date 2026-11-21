# ADR-009 — Preserve failed attempts and reuse passed handoffs

## Status

Implemented in the local recovery harness. Stage restarts were verified
with offline fixtures.

## Context

In the five-issue validation, the provider rejected three byte-identical
strict-schema requests that had previously succeeded. Two other runs
reached Design. They stopped on a defective draft or missing public-test
evidence. Restarting every predecessor would repeat calls and obscure
which change the recovery actually tested.

## Decision

After a provider JSON-validation rejection, try text output once and
apply the existing local structural validator. When the Requirements
quality gate rejects a proposal, return its public judgment to the
Planner once. Preserve pauses for material ambiguity. Provide pinned
source text search and accept equivalent numbered test mappings while
still requiring every acceptance criterion.

A restart may reuse each consecutive passed handoff from a parent
controller run that has the same issue, issue snapshot, application
revision and execution mode. Copy the handoffs into a new attempt and
record where they came from.

## Consequences

The recovery has a bounded cost, and unsuccessful attempts remain
available for evaluation. A structurally valid response can still be
incorrect. Design and Testing gates still control advancement.
