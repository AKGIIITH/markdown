# ADR-014. Recover a rejected final Builder submission

## Status

Accepted. Extends ADR-012 and ADR-013.

## Context

During the issue 3 demo, Groq rejected a file lookup on the last Builder turn.
That turn offered only the submission tool. A live retry with a forced tool
name produced the same rejection.

## Decision

Keep the lookup budget. If Groq rejects tool use on the submission-only turn,
make one paced text-completion request with the task input and latest tool
evidence. Pass that artifact through the existing edit, compile and test gates.
When the model quotes a block with relative indentation, restore a common
source prefix only if the resulting text has a unique match.

## Consequences

A recovery costs one additional provider call and a quota interval. The
recovered issue 3 patch compiled and passed four public acceptance tests and
three private tests locally. Other provider errors and ambiguous edit anchors
still stop the stage. The maintainer verifies publication and review on the
default branch before counting a hosted success.
