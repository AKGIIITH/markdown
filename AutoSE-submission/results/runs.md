# Runs, pull requests and reviews

## Hosted issue-triggered baseline

| Issue | Actions run | Last model gate |
| --- | --- | --- |
| 1 | [44633946770](https://github.com/AKGIIITH/markdown/actions/runs/44633946770) | Requirements provider format error |
| 2 | [44634053271](https://github.com/AKGIIITH/markdown/actions/runs/44634053271) | Requirements provider format error |
| 3 | [44632999808](https://github.com/AKGIIITH/markdown/actions/runs/44632999808) | Design draft exceeded its completion cap |
| 4 | [44634182887](https://github.com/AKGIIITH/markdown/actions/runs/44634182887) | Requirements provider format error |
| 5 | [44634287166](https://github.com/AKGIIITH/markdown/actions/runs/44634287166) | Material ambiguity |

## Guided candidates

| Issue | PR | CI and review |
| --- | --- | --- |
| 3 | [PR 6](https://github.com/AKGIIITH/markdown/pull/6) | No CI run observed. Review pending. |
| 2 | [PR 13](https://github.com/AKGIIITH/markdown/pull/13) | [Matrix passed](https://github.com/AKGIIITH/markdown/actions/runs/44789153426). [Changelog required](https://github.com/AKGIIITH/markdown/actions/runs/44789153616/job/136471891273). Review stayed gated. |
| 3 | [PR 15](https://github.com/AKGIIITH/markdown/pull/15) | [Initial CI](https://github.com/AKGIIITH/markdown/actions/runs/44810387807), [formatting retest](https://github.com/AKGIIITH/markdown/actions/runs/44811083687), [passing final CI](https://github.com/AKGIIITH/markdown/actions/runs/44811501466), [posted review](https://github.com/AKGIIITH/markdown/pull/15#pullrequestreview-5998959116). |

The independent review on PR 15 requested a change based on a claim the
operator later contradicted by inspecting the exact head. It remains a
recorded change request.

## Blinded reviewer benchmark

| PR | Posted result |
| --- | --- |
| [8](https://github.com/AKGIIITH/markdown/pull/8) | [Approve](https://github.com/AKGIIITH/markdown/pull/8#pullrequestreview-5997230718) |
| [9](https://github.com/AKGIIITH/markdown/pull/9) | [Approve](https://github.com/AKGIIITH/markdown/pull/9#pullrequestreview-5997231514) |
| [10](https://github.com/AKGIIITH/markdown/pull/10) | [Request changes](https://github.com/AKGIIITH/markdown/pull/10#pullrequestreview-5997232164) |
| [11](https://github.com/AKGIIITH/markdown/pull/11) | [Request changes](https://github.com/AKGIIITH/markdown/pull/11#pullrequestreview-5997232817) |
| [12](https://github.com/AKGIIITH/markdown/pull/12) | No verdict |

## Demo configuration verification

| Issue | Public tests | Full suite | Private tests | Release preflight |
| --- | --- | --- | --- | --- |
| 2 | 5 passed on candidate, 2 failed on seed | 1,117 passed, 111 skipped in 1.61 s | 3 of 3 passed | `8220cfce9a13700b37ef0746d5b0bdb96e745493` |
| 3 | 4 passed on candidate, 3 errored on clean | 1,116 passed, 111 skipped in 1.62 s | 3 of 3 passed | `b1836150a10ff31626d5cdebe2acab8bcdfc5d75` |

These replays used recorded patches and generated tests with the new
changelog behavior. The separate LangGraph fixture replay of Issue 3
passed all four local stages. Both new bundles stayed local. The deployment,
container lint, and two new end-to-end runs require hosted verification.

## Model usage

| Batch | Reported tokens |
| --- | ---: |
| First guided Issue 3 pilot | 33,319 |
| Five hosted baseline runs | 28,618 |
| Three stage comparisons | 30,415 |
| Five selected-settings runs | 40,166 |
| Five bounded-recovery runs | 61,364 |
| Guided Issue 2 | 11,201 |
| Five blinded reviewer checks | 36,803 |
| Issue 3 public-failure repair experiment | 44,337 |
| LangGraph 20B live attempt | 5,083 |
| Issue 3 SDK trace | 5,662 |
| Issue 3 120B through Testing | 69,339 |
| Independent Issue 3 review | 6,213 |
| **Known reported total** | **372,520** |

Totals use the documented batch receipts. Provider errors and exploratory
calls with no receipt leave total actual usage uncertain. Local replays
and preflight used no provider calls.

## Follow-up on Issues 1, 4, and 5

| Issue | First hosted stop | Later live stop | Pinned application probe |
| --- | --- | --- | --- |
| 1 | Requirements provider JSON error | Requirements accepted three testable criteria and asked how to serialize the enabled attribute. | The ordinary Python fence renders. Valueless and explicit true forms both raise the reported serialization error. |
| 4 | Requirements provider JSON error | Requirements asked about exact option semantics, matching, heading levels, and IDs. | The pinned TOC extension rejects the proposed option as unknown. |
| 5 | Requirements material ambiguity | Requirements accepted a clear error and nonzero exit. Design exhausted its lookup calls before reading a test. | A missing input exits with status 1 and prints a traceback. |

The follow-up repaired the Design reader. The previous configuration supplied
pinned starting ranges for Issues 2 and 3, but the reader still entered
the lookup loop without loading those ranges. All five issues now load
bounded source and public-test excerpts before the Design writer call.
Simulated responses passed that handoff for all five. The Issue 3 lookup
fixture also reached Testing and passed. The Issue 1 public snapshot now
includes the fenced syntax needed to reproduce the crash.

For Issues 1 and 4, a maintainer clarification can resolve Requirements before
the next hosted run. For Issue 5, the public CLI tests are now visible to Design.
The original brief still allows the Requirements gate to ask about scope.
These checks validate failure reproduction and Design input, with no new live
model output or published candidates for the three issues.

## Continuation from the failed terminal demo

| Issue | Saved starting point | Candidate | Hosted checks |
| --- | --- | --- | --- |
| 2 | [Design passed before the Builder exceeded its prompt budget](https://github.com/AKGIIITH/markdown/actions/runs/44896921009). The compact submission removed the two lines causing the separator regression. | [PR 22](https://github.com/AKGIIITH/markdown/pull/22) | [Application CI passed](https://github.com/AKGIIITH/markdown/actions/runs/44899108239). |
| 3 | [Requirements paused on two excluded cases](https://github.com/AKGIIITH/markdown/actions/runs/44897356445). After the corrected requirements passed, Design and Builder continued from the saved evidence. Public tests exposed a configuration type error. | [PR 24](https://github.com/AKGIIITH/markdown/pull/24) | [Initial lint failure](https://github.com/AKGIIITH/markdown/actions/runs/44904246145). After adding the missing newline to the generated test file, [CI passed on the same PR](https://github.com/AKGIIITH/markdown/actions/runs/44904880505). |

These were operator-guided stage continuations. The original issue workflows stopped before publication. Each candidate passed three private tests. The full local suite recorded 1,117 passes for issue 2 and 1,116 for issue 3, with 111 skips each. Fresh local GPT-OSS 120B reviews approved the verified heads of PRs 22 and 24. Each reviewer saw the public issue, diff, and pinned repository. Local review had no Docker runner. Hosted review posting requires the separate reviewer identity.

## Verified hosted demo reviews

Both open candidates passed CI. The resumed review jobs ran the isolated suite, inspected the candidate source, and posted the independent verdict on the exact head. The two successful review jobs used one Groq call each.

- Issue 2, commit `8220cfce9a13`, 2,522 review tokens. [Candidate](https://github.com/AKGIIITH/markdown/pull/28) · [Actions run](https://github.com/AKGIIITH/markdown/actions/runs/44909448352) · [Posted APPROVE verdict](https://github.com/AKGIIITH/markdown/pull/28#pullrequestreview-6005531163)
- Issue 3, commit `2d1b5c42050b`, 3,345 review tokens. [Candidate](https://github.com/AKGIIITH/markdown/pull/29) · [Actions run](https://github.com/AKGIIITH/markdown/actions/runs/44909670652) · [Posted APPROVE verdict](https://github.com/AKGIIITH/markdown/pull/29#pullrequestreview-6005551412)
