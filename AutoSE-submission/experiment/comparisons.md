# A, B, and C stage comparisons

These were live stage-level comparisons on Groq Free with
`openai/gpt-oss-20b`, temperature zero, and the baseline completion caps.
They reused saved inputs and did not modify a deployed run. Each condition
was tried once per listed issue.

| Comparison | Control | Variant | Decision |
| --- | --- | --- | --- |
| A. Requirements output contract | JSON object mode rejected the initial proposals for Issues #1, #2, and #4 | Strict schema produced three valid proposals. Issue #2 advanced; Issues #1 and #4 paused for clarification. | Select strict schema for the proposal. Keep the independent quality check. |
| B. Design writer evidence | On Issue #3, broad excerpts used 4,407 prompt and 4,000 completion tokens and produced an empty draft | Focused excerpts used 3,585 prompt and 3,235 completion tokens and produced a complete draft that failed the gate | Leave the Design default unchanged. |
| C. Builder testing context | Retaining the implementation response produced two candidate failures | Omitting that response produced three candidate passes and two expected clean errors | Select patch-only context for test generation and retain the option to replay the baseline. |

## A. Requirements output contract

Only the proposal response format changed. The scope and format checks stayed
in place, and the quality check used the same request settings on each valid
proposal. The experiment separated provider JSON errors from maintainer pauses.
Issue #1 paused on the value of the `linenums` attribute. Issue #4 also raised
a blocking question. The comparison covered the three earlier provider
failures. It does not estimate the pass rate on all issues.

| Issue | Proposal | Full Requirements | Reported tokens |
| --- | --- | --- | --- |
| 1 | Valid | Paused | 5,047 |
| 2 | Valid | Passed | 5,145 |
| 4 | Valid | Paused | 6,415 |

## B. Design writer evidence

The variant selected shorter pinned ranges covering table construction,
registration, option parsing, and a public API example. It used the same
issue, accepted specification, architecture, model, reasoning default and
4,000-token cap as the hosted writer. It reduced reported tokens from 8,407
to 6,820 and finished with `stop`. The evaluator rejected its test-mapping
format. The proposal also selected a `None` default that the pinned option
parser would treat as boolean-like. No Design handoff was accepted.

## C. Builder testing context

The test generation requests differed only in whether the preceding
implementation response was included. Both retained the accepted pilot
handoff, production diff and public test example. The retained condition used
3,530 tokens and passed configuration in a way Markdown ignored for an
already-instantiated extension. Both clean and candidate runs had two
failures. The clean full suite passed after removing the new tests.

The omitted condition used 3,458 tokens. Its tests passed on the candidate
and the full suite had 1,115 passes and 111 skips. Reversing CSS token order
preserved the result. The tests also accepted output containing two copies
of the first table, exposing a distinct-table coverage gap. No new private
evaluation was performed. Both conditions used the same frozen production
patch.

The experiments used 30,415 reported tokens across nine provider responses.
The baseline's three rejected responses still have unknown usage.
