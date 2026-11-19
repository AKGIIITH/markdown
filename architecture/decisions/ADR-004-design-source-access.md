# ADR-004 — Let the Planner inspect pinned public source during Design

## Status

Accepted for the baseline. The tool exchange has been verified with simulated
replies.

## Context

The Issue #3 pilot depended on the operator choosing source excerpts. The
first design missed the behavior of a configuration helper. The architecture
document provides useful starting points, and the pinned source determines
what the application actually does.

## Decision

Give the Design Planner the application architecture, the issue and the
accepted requirements. It can list public application files by prefix, search
for a filename in application source or public tests, and read bounded line
ranges at the application's pinned revision. The controller
executes the reads and records each request and result. A caller-supplied
model-call budget bounds the conversation. Design must cite both inspected
application source and a public test and map every accepted criterion to a
public test entry.

## Consequences

The Planner can follow evidence across files without a maintainer selecting
each excerpt. Each lookup adds context and may require another model call.
The bound makes those costs measurable. The tools provide no write access,
shell execution or private-test access. An incomplete design fails the
Design gate and keeps the draft for diagnosis.
