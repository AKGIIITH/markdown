# ADR-001 — Assign the six workflow stages to three agent roles and a release script

## Status

Accepted for the baseline.

## Context

Requirements and design depend on the same interpretation of the issue.
Implementation and testing share a working checkout. When a test fails,
the Builder benefits from knowing which change it just made and why.
Review has a different purpose. The Reviewer needs to judge the patch
against the issue and form its own explanation of any defect.

## Decision

| Stage | Owner | Responsibility |
|---|---|---|
| Requirements | Planner | Read the issue, apply the A1 skill, and write observable acceptance criteria in `spec.md`. |
| Design | Planner | Continue from the accepted specification, inspect the source and A2 architecture document, and record the proposed changes in `design.md`. |
| Implementation | Builder | Start a fresh conversation with the issue, accepted specification, design, and working checkout. Implement the change. |
| Testing | Builder and test runner | The Builder retains recent implementation history, writes tests for the criteria, and repairs failures. The runner executes the tests and records actual outcomes. |
| Release | Release script | Push the tested revision, open or reuse the PR against the designated base, and verify CI on the current PR head. These operations use inputs the controller already knows. |
| Review | Independent Reviewer | Start a fresh conversation for each review round. Inspect the issue, PR diff, and source at the PR head. Run checks as needed and return a verdict. A human decides whether to merge. |

The controller manages conversation history. When a Builder run resumes
after interruption or its conversation grows too large, the controller
restores the accepted specification, design, current checkout, and latest
test results. Roles may use the same model ID. Each role receives only
the context and tools needed for its task.

## Consequences

Keeping implementation and testing together may reduce repeated file
reads and help the Builder repair a failing assertion. It also creates a
risk that the Builder will encode the same mistaken assumption in both
the code and its tests.

We will record Builder token usage and repair attempts to measure the cost
of carrying context forward. We will compare the Builder's test results
with independent review findings and private acceptance-test outcomes to
identify defects its own tests missed. Fresh review context reduces the
influence of the Builder's rationale, although agents using the same
model can still make similar mistakes.
