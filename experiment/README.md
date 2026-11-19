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
heads, and the two-round review cap. No hosted run has exercised these jobs.

## Deployment and evaluation status

| Work | Status |
| --- | --- |
| Issue trigger, Requirements through Testing, Release bundle | Implemented and replayed locally with fixtures |
| Publication, exact-head CI gate, Reviewer and review posting | Implemented and exercised with offline GitHub and model fixtures |
| Review changes return path | The poster records the responsible stage and next round. Automatic execution of the repair and updating the same PR remain pending. |
| Hosted baseline for five issues | Pending activation and runs |
| Experiments and final evidence | Two ADR experiments await selection after baseline observations. Reviewer-check PRs, aggregate results, report and demo remain pending. |

The fork's protected `main` must contain the workflow before issue events
can start it. Publication and review are opt-in. Deployment uses the
`GROQ_API_KEY`, `AUTOSE_RELEASE_TOKEN`, and `AUTOSE_REVIEW_POST_TOKEN`
repository secrets with the approved `AUTOSE_*` budget variables.
The release credential needs repository content and PR write access. The
posting credential needs PR write access and an identity separate from the
PR author. The reviewer job itself receives a read-only GitHub token. The
workflow has no merge step.
