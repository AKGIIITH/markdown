# AutoSE baseline evidence

The application revision and the harness revision are tracked independently.
These before-change measurements came from a separate private evaluation.

| Issue | Application revision | Before-change result |
| --- | --- | --- |
| [1](https://github.com/AKGIIITH/markdown/issues/1) | `2c96e36` | 1 pass, 2 errors |
| [2](https://github.com/AKGIIITH/markdown/issues/2) | `1e2b7f2` seeded | 2 passes, 1 assertion failure |
| [3](https://github.com/AKGIIITH/markdown/issues/3) | `2c96e36` | 1 pass, 2 errors |
| [4](https://github.com/AKGIIITH/markdown/issues/4) | `2c96e36` | 1 pass, 2 errors |
| [5](https://github.com/AKGIIITH/markdown/issues/5) | `2c96e36` | 2 passes, 1 failure |

The Issue #2 clean revision passed all three private cases. The before-change
suite above contains 15 cases in total. It measures the application baseline.

## Guided pilot

Issue #3 was run with manual source and handoff corrections. The first
Requirements call preceded the architecture commit. Groq produced the
production patch and initial tests. Codex strengthened a test assertion after
demonstrating a duplicate-table blind spot. The final guided patch passed all
three public acceptance tests and all three private evaluation tests. The local
suite had 1,115 passes and 111 skips.

The tested revision was published in [PR #6](https://github.com/AKGIIITH/markdown/pull/6).
GitHub confirmed the head SHA. CI did not register a run during the observed
polling windows. The PR is open and independent review remains pending.

The later live Design validations exercised source lookup and a separate
writer. Filename search let the lookup phase find and read a public test.
The writer either truncated or returned a defective design. The subsequent
guided Builder validation returned source edits with line-number annotations
inside its search strings. The matching gate rejected both edits before
compilation and test generation.

## Workflow implementation evidence

The offline controller replay uses a recorded Requirements proposal, simulated
quality and Design replies, and recorded Builder artifacts. It advances
through Testing and reproduces the before-and-after suite results without
provider calls. A separate Release preflight rebuilds the candidate from the
verified patch digest and creates a Git bundle for the tested commit.

The GitHub Actions source accepts an `autose:run` issue label or an exact
`/autose run` issue comment from an authorized maintainer. Its preparation
and test jobs use separate permissions and artifacts. Hosted execution
requires the workflow on the default branch and the approved Groq secret and
budget variables. The release job verifies the pinned fork and base and opens
or reuses a PR for the tested head. A read-only job verifies CI before starting
independent review. Review posting is a separate job. Offline responses
exercised PR creation and reuse, absent CI, an incomplete CI matrix, stale PR
heads, and the two-round review cap. No hosted run has reached those jobs.

## Hosted baseline runs

| Issue | Run | Requirements | Design | Implementation and Testing | Known tokens |
| --- | --- | --- | --- | --- | --- |
| [1](https://github.com/AKGIIITH/markdown/issues/1) | [44633946770](https://github.com/AKGIIITH/markdown/actions/runs/44633946770) | Provider JSON validation error | Skipped | Skipped | Unknown |
| [2](https://github.com/AKGIIITH/markdown/issues/2) | [44634053271](https://github.com/AKGIIITH/markdown/actions/runs/44634053271) | Provider JSON validation error | Skipped | Skipped | Unknown |
| [3](https://github.com/AKGIIITH/markdown/issues/3) | [44632999808](https://github.com/AKGIIITH/markdown/actions/runs/44632999808) | Passed | Failed at handoff writing | Skipped | 24,733 |
| [4](https://github.com/AKGIIITH/markdown/issues/4) | [44634182887](https://github.com/AKGIIITH/markdown/actions/runs/44634182887) | Provider JSON validation error | Skipped | Skipped | Unknown |
| [5](https://github.com/AKGIIITH/markdown/issues/5) | [44634287166](https://github.com/AKGIIITH/markdown/actions/runs/44634287166) | Paused for material ambiguity | Skipped | Skipped | 3,885 |

All five attempts used the workflow on `main` at `4d8aeea` and passed
trigger authorization. Requirements passed one of five runs. Three provider
responses returned `json_validate_failed` with empty failed generations and
unreported usage. The quality check paused Issue #5 on the exact exit code,
the error message, and whether traceback suppression should extend to other
errors.

Design ran once. It collected pinned source and public-test excerpts, then
its writer hit the 4,000-token cap with 3,753 reasoning tokens and an empty
draft. Implementation and Testing were skipped on all five issues, and no
hosted candidate reached private evaluation. Publication and review were
disabled for this batch. Known usage was 28,618 tokens across nine distinct
provider responses, plus three attempts with unreported usage.

## Deployment and evaluation status

| Work | Status |
| --- | --- |
| Issue trigger, Requirements through Testing, Release bundle | Implemented and replayed locally with fixtures |
| Publication, exact-head CI gate, Reviewer and review posting | Implemented and exercised with offline GitHub and model fixtures |
| Review changes return path | The poster records the responsible stage and next round. Automatic execution of the repair and updating the same PR remain pending. |
| Hosted baseline for five issues | All five attempts recorded. No run reached Implementation. |
| Experiments and final evidence | Three stage comparisons and five blinded reviewer checks recorded. See the report and demo. |

The [stage comparisons](comparisons.md) select strict Requirements schema
and patch-only Builder testing context for the next configuration. The
deployed baseline remains available as the comparison control.

## Selected settings validation

The selected configuration at `b7ed127` was then run locally with live Groq
requests on the five original public issue snapshots. Issues #1, #2 and #4
received the same provider JSON-validation error from byte-identical requests
that had succeeded during the format experiment. Issues #3 and #5 passed
Requirements and stopped in Design. Issue #3 produced a defective draft;
Issue #5 ran out of lookup calls without reading a public test.

No run reached Builder and no new candidate was frozen. The five runs used
40,166 reported tokens across 13 responses, with three unreported attempts.
This validation used the selected local harness. It did not replace the
recorded hosted baseline.

The Release check independently verified the five real fork targets and
reconstructed a tested Issue #3 Git bundle. A simulated GitHub API exercised
PR creation and reuse with the exact tested head. The real fork had automatic
publication disabled and no release credential, so this check sent no writes.

## Bounded recovery validation

All five local recovery attempts produced structurally valid Requirements
proposals. Issues #1 and #4 paused for clarification. Requirements passed
on Issues #2, #3 and #5. Design stopped at missing public-test reads for
Issues #2 and #5 and at an uncited public-test excerpt for Issue #3.
Implementation was skipped in all five. The batch reported 61,364 tokens,
with one provider response unreported.

The recovery adds a text fallback for provider JSON-validation errors,
literal search of pinned public source and tests, and support for equivalent
numbered Design mappings. The [recovery ADR](../architecture/decisions/ADR-009-recovery-and-restart.md)
also records the one-step Requirements repair and restart policy.

## Additional guided pilot and reviewer benchmark

[PR #13](https://github.com/AKGIIITH/markdown/pull/13) targets the seeded
Issue #2 base `a3/bug02-seed` at tested head `c4d344d`. Groq proposed
deleting the seeded separator override, but its surrounding text did not
match the file. Codex applied just the proposed deletion in a separate
attempt and authored five public tests. Two failed on the seed and all five
passed on the candidate. The full suite had 1,117 passes and 111 skips.
The frozen candidate passed all three private checks. Eleven GitHub checks
passed for the same published revision. The changelog check failed because
the candidate left `docs/changelog.md` untouched. The release script recorded
`ci_failed` and the normal review gate stayed closed.
See the [failed GitHub check](https://github.com/AKGIIITH/markdown/actions/runs/44789153616/job/136471891273).

The five [blinded reviewer checks](reviewer-results.md) produced two
correct verdicts, two incorrect verdicts and one unavailable verdict.
Four model findings were posted as review comments on the exact draft heads.
The benchmark's private oracle labels were withheld from all model inputs.

The [report](report.pdf), [demo](demo.mp4), and [submission URL](../submission.txt)
are packaged with this evidence.

The fork's protected `main` must contain the workflow before issue events
can start it. Publication and review are opt-in. Deployment uses the
`GROQ_API_KEY`, `AUTOSE_RELEASE_TOKEN`, and `AUTOSE_REVIEW_POST_TOKEN`
repository secrets with the approved `AUTOSE_*` budget variables.
The release credential needs repository content and PR write access. The
posting credential needs PR write access and an identity separate from the
PR author. The reviewer job itself receives a read-only GitHub token. The
workflow has no merge step.
