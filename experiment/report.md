# Issue In, Pull Request Out

## Workflow

A maintainer applies `autose:run` or comments `/autose run` on an open issue
in the fork. The controller verifies the event and maintainer permission,
selects the issue's pinned application commit, and records the harness revision
separately. The workflow assigns Requirements and Design to the Planner,
Implementation and Testing to the Builder, Release to a trusted script, and
Review to an independent Reviewer.

Requirements uses the A1 skill and a separate quality judgment. The Design
Planner receives the accepted specification and architecture and performs
bounded reads of pinned public source and tests. A fresh writing request
produces the Design handoff. The Builder produces exact source edits and a
public test module. The test runner compares the same tests on clean and
candidate source and runs the candidate's public suite.

Release reconstructs the passed patch, checks the target and exact commit, and
opens or reuses a PR. The CI gate checks the published head and its generated
merge commit. The Reviewer starts with the issue, PR diff and pinned source.
It can run public checks in an isolated container. A separate job posts
findings. The workflow leaves merge to the maintainer.

## Evaluation method

The five cases include a real rendering bug, a seeded TOC regression, two
features, and an underspecified CLI error. The pre-change private evaluation
ran 15 tests, with seven passes, two assertion failures and six errors.
Issue #2 used a separate seeded commit, and its clean counterpart passed all
three private tests.

The hosted baseline uses the same Groq model, temperature and caps on each
issue. Each stage is recorded as passed, failed, or skipped. A later stage
that never runs contributes no observed outcome for that stage. Token
reporting deduplicates successful responses by ID and keeps unreported usage
separate. Private evaluation applies to frozen candidates and is excluded
from model inputs. The guided Issue #3 pilot is reported separately from
hosted autonomous runs.

## Guided pilot

The first Requirements experiment preceded the architecture commit. The
operator selected source and corrected the Design handoff in the subsequent
pilot. Groq wrote the production patch and the initial tests. The operator
detected that the tests accepted a duplicate table and strengthened their
assertions. The final public tests passed on the candidate and detected the
missing option on clean source. The full local suite had 1,115 passes and
111 skips. Separate private evaluation passed all three cases.

The tested candidate is open in [PR #6](https://github.com/AKGIIITH/markdown/pull/6).
The release script verified its published head. GitHub did not register a CI
run during the pilot's verification windows.

## Hosted baseline, experiments, and reviewer checks

All five hosted attempts used the same workflow revision and passed trigger
authorization. Requirements passed one of five. Groq rejected three
initial proposals with JSON-validation errors, and the quality check paused
the vague CLI issue for maintainer input. Design was reached once. Its
writing request used all 4,000 completion tokens and produced an empty
draft. No run reached Implementation or Testing. Delivery through Testing
was zero of five. These denominators distinguish stages that failed from
stages that never ran.

The five attempts used 28,618 reported tokens, plus three provider responses
with unreported usage. Real run links, per-issue results and skipped stages
are in the [experiment ledger](README.md).

The maintainer selected three [stage comparisons](comparisons.md). Strict
Requirements schema recovered all three structurally invalid proposals.
One passed the full stage and two paused for clarification. Focused Design
evidence let the writer finish under the same cap, but the draft failed the
gate and proposed a defective default. Patch-only context yielded passing
public tests and a green full suite on the frozen Issue #3 candidate. An
additional probe showed that those tests would accept duplicate tables.

The next configuration uses strict schema and patch-only testing context.
Design remains unchanged. The comparisons measured one response per
condition and issue, so they do not establish a general performance
difference. They consumed 30,415 reported tokens, separately from the hosted
baseline.

## Validation of the selected configuration

Five local live attempts used the original issue snapshots and selected
settings. Two passed Requirements and neither passed Design. Groq rejected
the other three Requirements requests despite receiving their byte-identical
strict-schema experiment inputs. For Issue #3 the writer finished but still
proposed a defective configuration default. For Issue #5 the Planner
exhausted its lookup budget without reading a public test. The runs reported
40,166 tokens, plus three unreported attempts. They produced no new frozen
candidate.

A frozen candidate is a commit reconstructed from the pinned issue-bearing
revision, the production patch and public tests after Testing passes. Its
build, private evaluation and release can be traced to the exact tested
content. Read-only GitHub checks confirmed the target branches for all five
issues. A Release replay reconstructed a tested bundle and exercised PR
creation and reuse through a simulated API. The real publishing job was
disabled for the validation run.

## Recovery and restart

The local recovery harness uses one text fallback after a rejected JSON
response and retains local structure checks. Design gained pinned source
text search and recognizes equivalent numbered test mappings. A Requirements
quality rejection can return to the Planner once. A restart can reuse passed
handoffs bound to the same issue snapshot and application base.

All five recovery proposals passed structural validation. Issues #1 and #4
paused for clarification. Issues #2 and #5 stopped without a public-test
read, and Issue #3 stopped because its completed draft did not cite the
public test it read. No autonomous recovery run reached Implementation.
Known usage was 61,364 tokens, plus one unreported response.

## Guided Issue #2 recovery

The operator provided pinned source ranges and a public test excerpt after
the autonomous Design lookup stopped. Groq proposed deleting the override
that converted a tilde into a hyphen. The proposed surrounding text
contained an unrelated mismatch. Codex preserved that failed attempt,
re-anchored only the proposed deletion, and authored five public tests.
They check the three heading IDs and the two TOC links' matching HTML
targets. The tests verify link resolution in rendered HTML.

The seeded revision had three public passes and two failures. The tested
candidate had five public passes, 1,117 suite passes, and 111 skips. It
passed all three private tests. The trusted publisher opened
[PR #13](https://github.com/AKGIIITH/markdown/pull/13) against the distinct
seeded base at frozen head `c4d344d`. The guided model calls reported
11,201 tokens. Eleven GitHub checks passed on that revision. The
changelog-enforcer failed its `check-for-entry` job. The tested diff changes
application code and leaves `docs/changelog.md` untouched, which triggers
that check. The release script recorded `ci_failed`, so the normal review
gate did not open. The PR remains open.

[GitHub CI check](https://github.com/AKGIIITH/markdown/actions/runs/44789153616/job/136471891273).

## Blinded Reviewer

Five real draft PRs used two passing controls and three planted defects.
The oracle was kept outside model context. The Reviewer saw the public
Issue #3, the PR diff and the exact source revision. Two of the first five
attempts produced a verdict. One bounded writer-only recovery per missing
verdict kept the cap fixed and reduced reasoning effort.

The final results were two correct verdicts, two incorrect verdicts and
one unavailable verdict. The incorrect verdicts included one false approval
and one false change request. The Reviewer detected one of three defects.
Four findings were posted as GitHub review comments because the posting
account opened the drafts. The unreturned verdict was recorded as
`NO_VERDICT`. The complete benchmark reported 36,803 tokens, with one
provider attempt unreported.

[Reviewer draft #8](https://github.com/AKGIIITH/markdown/pull/8),
[Draft #9](https://github.com/AKGIIITH/markdown/pull/9),
[Draft #10](https://github.com/AKGIIITH/markdown/pull/10),
[Draft #11](https://github.com/AKGIIITH/markdown/pull/11),
[Draft #12](https://github.com/AKGIIITH/markdown/pull/12).

## GPT-OSS 120B follow-up

Near the deadline, the maintainer chose GPT-OSS 120B on the same Groq Free
project and retained the per-call caps. Two Requirements runs passed
structural validation and paused over scope. The maintainer clarified the
scope and approved the unchanged criteria. The LangGraph controller passed
that artifact to Design and then Builder. Codex fixed the Design checker
to accept bold criterion numbers and revalidated the unchanged draft.

Groq rejected a long test submission because the request exceeded the
free-tier per-minute token limit. Shorter subsequent requests produced
usable tests after corrections prompted by public runtime evidence. The
model identified an empty-string default for the configuration API. Codex
composed the model's exact candidate-relative edit with its earlier patch.
The final generated tests passed four of four on the candidate, detected
the missing feature on clean source, and gave 1,116 full-suite passes and
111 skips. Separate private evaluation passed all three cases.

The trusted publisher opened [PR #15](https://github.com/AKGIIITH/markdown/pull/15).
The first head passed the changelog check, and two style checks flagged the
generated tests. Codex corrected blank lines and two references in one
docstring, verified that executable test logic was identical, retested,
and fast-forwarded the PR. The final head passed all three private checks
and GitHub CI.
The experiment through Testing used 69,339 known model tokens, plus one
rejected request of unreported usage. See the [full follow-up trace](issue-3-120b.md).

An independent GPT-OSS 120B review used 6,213 tokens and requested
Implementation changes. The PR already passed configuration to the table
processor, and GitHub CI passed. The [review comment](https://github.com/AKGIIITH/markdown/pull/15#pullrequestreview-5998959116)
preserves the false change request with the separate operator verification.

## Limitations

No hosted autonomous run produced a candidate. The improved workflow was
checked locally in fixtures and live stage runs. The guided fixes do not
count as autonomous deliveries. The ordinary workflow verifies CI before
review, while the blinded benchmark deliberately tests Review independently
against draft PRs. The workflow records the responsible stage after a
review asks for changes. Automatic second-round repair on the same PR
remains to be wired and validated. All experiment and guided application PRs remain
open for the maintainer.

## AI-use disclosure

Groq `openai/gpt-oss-20b` is the system under evaluation. Codex contributed to
harness implementation, operations, draft documentation, and the explicitly
recorded pilot corrections. The maintainer selected the architecture and
approved substantive changes and live budgets. Manual, simulated, and hosted
autonomous evidence are identified separately. The demo uses synthesized
narration over the recorded results.

## Demo hardening and hindsight

The hosted demo configuration selects GPT-OSS 120B. Design uses the
architecture and curated starting ranges from pinned public source and
tests for Issues 2 and 3. Other issues retain bounded lookup tools.
LangGraph keeps Implementation and Testing in separate tasks, with
a single focused Planner clarification available to the Builder.

| Decision | Why it was retained or revised | Evidence |
| --- | --- | --- |
| Shared Planner, isolated Reviewer | Share domain context within Planning while avoiding implementer anchoring in Review. | The blinded Reviewer scored two of five correctly and made a false change request on PR 15. |
| Separate Design lookup and writing | Keep large tree searches outside the final writing call. | Focused excerpts improved completion but still needed a grounded handoff gate. |
| Patch-only Testing context | Keep the public API examples and exact change in the test writer's inputs. | Comparing the two contexts revealed different test defects and a smaller request with the patch. |
| Per-call pacing and small tasks | Fit the measured quota and keep a 60-second reset interval. | The former combined request reserved 8,291 tokens against the reported 8,000 limit. |
| Check spelling and style before Release | Expose predictable CI failures alongside test failures and repair before publishing. | PR 13 missed a changelog entry, while PR 15 needed whitespace and a spelling correction. |

The local replays produced two changelog-complete Release bundles. Issue 2
had 1,117 passes and 111 skips. Issue 3 had 1,116 passes and 111 skips.
Each candidate passed all three private acceptance tests. The timed
candidate suites took about 1.6 seconds each. These were artifact replays.

The demo should begin with a run on Issue 2, followed by Issue 3. Record
the new Actions run, exact PR commit, and review. A change request now
has a hosted round-two route after the maintainer changes the same PR.
The hosted repair and fresh round-two route need live verification.
There is no automatic application of review-driven fixes.

The [token ledger](../results/runs.md) records 372,520 reported tokens from the
documented batches, with remaining usage unknown. Earlier writing should
have been bounded before calling the provider. Pre-publication lint and a
required independent CI check would have avoided presenting PR 13 and the
first heads of PR 15 as ready for review.

## Appendix. Threats to validity

**Construct validity.** Public gate success measures whether the model's
tests pass and detect a change against a prior revision. It can miss the
maintainer's intended behavior, unexplored cases, and tests that pass for the
wrong reason. Separately controlled private tests provide a stronger signal,
but three checks per issue leave substantial behavior unmeasured. Reviewer
verdicts measure agreement with the recorded oracle on five selected PRs.
The false findings on the real table PR show why line citations and test
evidence matter.

**Internal validity.** The guided pilots included scope clarification,
source selection, exact-patch composition, test authoring, and formatting
repairs. Their success cannot isolate the effect of the model size, the agent
graph, or the token pacing policy. Provider format errors and quota
exhaustion censored some stages before an answer. The stage comparisons
used comparable inputs, but repetitions and condition order were limited.
Transport and tool availability changed during the experiments.

**External validity.** One mature Python package, five issues, and one
provider do not establish performance across repos, languages, test runners,
quotas, or issue complexity. Issue 2 is a targeted synthetic regression.
The deterministic Design starting ranges are specific to the two demo
cases. Larger changes may need several implementation tasks with narrower
artifacts and stronger dependency validation.

**Operational validity.** The full suite passed locally against the two
replayed candidate revisions. The ready-to-publish bundle and exact-head
checks preserve what is tested. Docker execution, deployment, publication,
and round-two review on the updated workflow still require a hosted run.
GitHub free-runner availability and provider quotas can change timing.
Given slow calls, retries or a test repair, a live demo will need edited
waiting time. Protecting the base and securing the provider cap are
maintainer-side configuration tasks.
