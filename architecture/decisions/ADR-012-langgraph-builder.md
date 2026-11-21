# ADR-012 — Add a bounded LangGraph Builder

## Status

Experimental. A scripted replay passed Testing and Release preflight. A live
Groq replay completed a pinned read and then stopped at the provider's daily
token limit. The hosted baseline still uses the original Builder.

## Context

The Issue #3 Builder implemented a coherent plan with an incorrect
configuration default. Runtime tests revealed the error. Public feedback
then helped the same model repair it. The maintainer requested a coding
agent SDK and a way for Builder to question the plan before submission.

## Decision

Use LangGraph for an optional Builder backend. Reuse the current Groq
request path, per-call caps and attempt logging. Register bounded read-only
public lookup tools, a focused Planner question, and artifact submissions.
Charge the Planner answer to the Implementation call limit and reserve the
last call for submission. Keep patch application, compilation and test
execution in the existing trusted runners. A separate tool submission
ends each Builder task.

## Consequences

The model can inspect additional source and ask one question without
inventing a new test policy. The trace records the exact tool arguments and
answers. LangGraph supplies the dispatch loop, while the harness still
defines authorized actions and checks accepted artifacts. The extra turns
need an explicit budget for live evaluation. A successful scripted replay
measures integration; live comparisons measure model behavior.
