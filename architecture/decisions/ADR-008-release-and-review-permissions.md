# ADR-008 — Separate publication, verification, review, and posting permissions

## Status

Accepted for the baseline design. The handoffs have been exercised offline.

## Context

Release needs permission to publish a tested commit. A reviewer must judge
the change independently against the public issue and current source. GitHub
can report PR checks on the head or its generated merge commit.

## Decision

Use a trusted publisher to verify the fork, base, candidate tree, and head
before opening or reusing a PR. Verify CI in a read-only job and recheck the
current PR head. Start an independent Reviewer with the public issue and diff,
and access to that exact checkout. Run public checks in an isolated container.
Use a separate credential to post the actual result. Limit review to two
rounds and leave merging to the maintainer.

## Consequences

The reviewer cannot push changes or inherit the Builder's reasoning.
Missing CI leaves Review blocked. A changed head requires new CI and review
evidence. Separate credentials and job setup must be configured before a
hosted run can exercise publication and review posting.
