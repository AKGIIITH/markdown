# ADR-002 — Check the Planner's response structure and requirements quality before Design

## Status

Superseded by ADR-003 for the autonomous requirements-quality check. This
record preserves the original baseline decision and early pilot. The
provider and structural checks still apply.

## Context

The local requirements pilot for issue #3 ran before the architecture
commit. The saved request contained the intended A1 skill. Groq reported
`finish_reason=length` after 1,800 completion tokens, including 1,374
reasoning tokens.

The reply parsed as JSON and contained `summary` and `criteria`. It omitted
the required `unresolved` field, so the validator stopped the workflow
before Design. Inspection also found that one criterion required support
for an explicit `null` configuration value. The issue specified behavior
when the option was omitted and did not establish what an explicit
`null` should do.

## Decision

The controller records three findings separately.

| Check | Owner | Decision and evidence |
|---|---|---|
| Provider termination | Controller | Record the model ID, finish reason, and token counts. Preserve the original response so the termination evidence can be examined alongside the text received. |
| Response structure | Python validator | Require a nonempty summary, observable-criterion fields `given`, `when`, and `then` containing nonempty strings, and an `unresolved` array of nonempty question strings. An empty array is valid. A missing field fails validation. |
| Requirements quality | Maintainer during the baseline | Compare each criterion with the public issue. Check whether its outcome can be observed and whether the issue supports the behavior it requires. Record unsupported assumptions and questions that could change the design. |

Design can start when the response passes structural validation and the
maintainer accepts the criteria. If a question would change the required
behavior, record its resolution before accepting the specification.
Preserve failed attempts and link any revised specification to the
original response.

For issue #3, the missing `unresolved` field is sufficient to explain the
structural failure. The completion limit is a possible contributing
factor. The pilot alone cannot establish whether a larger allowance
would have prevented the omission.

## Consequences

The run log can distinguish a model reaching its token limit, a response
the controller cannot consume, and a well-formed criterion that expands
the task. This distinction helps us choose a later experiment based on
the failure actually observed.

Maintainer review adds time and judgment to the baseline. We will record
who performed it, which criteria needed revision, and whether the stage
advanced. This makes the human contribution visible when reporting
workflow autonomy and stage pass rates.
