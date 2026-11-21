# AutoSE on Python-Markdown

## 1. We started with five issues

We asked whether an issue could become a tested pull request while a maintainer kept the merge decision. We used the Python-Markdown fork because the public suite could run in seconds on the pinned checkout. We started with five public issue descriptions and kept three private checks per issue outside the repository. Difficulty below is our judgement about the work the description requires.

| Issue and origin | Type / difficulty | What a correct change would do |
| --- | --- | --- |
| 1. Fenced code; adapted from upstream #1713 | Real bug / medium | Render valueless and true linenums attributes without a serialization exception; preserve the code and language class. |
| 2. Heading links; authored seed | Bug / easy | With ~ configured, “Exam Notes” becomes exam~notes and the TOC link uses the same ID. Preserve defaults and explicit IDs. |
| 3. Table CSS classes; authored | Feature / small | Apply one or more configured classes to generated tables. Preserve cells, headers, raw HTML and output when omitted. |
| 4. Exclude selected headings; authored | Feature / medium | Hide a marked heading from the outline while keeping it linkable; promote its unmarked children in the right order. |
| 5. Missing input file; authored | Vague request / unclear | Give the CLI user a useful failure message and a failing exit status. The original brief leaves the exact contract open. |

The common application pin was 2c96e36. Case 2 used a separate seed, 1e2b7f2, which forced the tilde separator to a hyphen. The private baseline had 7 passes, 2 failures and 6 errors across 15 checks. A passing compatibility check before the fix is expected. We froze the candidate before private evaluation.

The first hosted batch advanced one issue through Requirements and none through Testing. After debugging and resuming from saved stages, cases 2 and 3 each reached an open candidate with green CI and a posted approval. Both are guided, resumed deliveries. We have no recorded uninterrupted issue-to-review success on this five-case batch.

Sources: the five briefs are in experiment/issues, the complete counts are in results/results.csv, and the final PRs are #28 and #29. The accompanying video shows a before-and-after conversion and the actual hosted review jobs.

## 2. How an issue reaches independent review

Our starting sketch had four jobs for six stages. The person interpreting a requirement should also plan where to change the code. The person writing the code needs the failing test and should be able to fix it. Opening a PR is a separate job; judging the result is another. Four jobs did not require four different model weights. ADR-001 records three model roles and a release script. Git already knows the tested commit, target and diff, so a model would add uncertainty to publication.

| Stage and owner | Handoff | Condition for moving on |
| --- | --- | --- |
| 1. Planner: requirements | spec.md, structured criteria, independent quality judgement | Every criterion has an observable outcome grounded in the issue. Pause on a material unresolved question. |
| 2. Planner: design | design.md and pinned excerpts | Name the source paths and symbols, and map criteria to public tests. |
| 3. Builder: implementation | diff.patch and build log | Apply exact edits on a new branch at the pin and compile. |
| 4. Builder and runner: testing | Public tests, final diff and test_report.md | Detect a regression on clean source; pass on candidate; pass existing suite and configured lint checks. |
| 5. Release script | pr.md, PR URL, head SHA, CI receipts | Rebuild the tested tree, open or reuse its PR, then verify CI on that head. |
| 6. Fresh Reviewer and poster | review.md, posted verdict, optional return stage | Approve or request changes. A changed head can be reviewed again, up to two rounds. Human decides merge. |

A maintainer's label or exact command starts GitHub Actions. Authorization occurs before the Planner receives issue text. The controller passes checked files between stages and records which gate stopped. Public issue text and source excerpts are treated as data. The test runner has no model or push credential. The review model gets the public issue, diff and repository at the PR head. A separate bot job posts the verdict as a comment review.

One observed sequence: issue 3 paused twice in Requirements. A revised proposal passed. Design named the table extension; Builder changed it. Tests exposed the default-type mistake. A repair passed public and private tests, then CI caught a missing newline. The fixed candidate was published again against a pinned base. On PR 29, the read-only reviewer ran the suite, inspected changed source and wrote its verdict; the bot posted it on commit 2d1b5c4. Saved checkpoints join these steps across several runs.

## 3. Which design decisions mattered most?

| Decision | Reason and trade-off |
| --- | --- |
| Divide the work by responsibility (ADR-001) | The Planner owns the meaning of the issue. The Builder owns code and tests. Sharing a role saves repeated explanation but can repeat the same wrong assumption. |
| Gate the specification (002–003) | A structured proposal can be valid JSON yet ask the wrong question. A separate call checks grounding and testability; that costs an extra call. |
| Read pinned public files (004–006) | Exact source and test examples reduce invented paths. Line numbers help inspection, but edit anchors need raw text without line labels. |
| Separate evaluation and release rights (007–008) | The Builder cannot read private tests or push. Release verifies the patch digest; the independent reviewer cannot change the code it judges. |
| Save handoffs and route failures (009, 011) | An HTTP error in test writing should not discard a compiled implementation. Receipts check the issue, revision and previous gate before reuse. Human intervention remains part of review repair. |
| Follow configuration dependencies (010) | The table extension's own file does not explain how the base Extension interprets defaults. The plan needs both the option and its setter. |
| Add bounded LangGraph calls (012) | Builder can inspect a public file or ask Planner one focused question, then return to submission. A fixed call budget prevents unbounded loops. |
| Pace requests and recover submissions (013–014) | Reserve room for output, wait on provider quota and keep the latest useful lookup. Protect exact edit and test checks even when a tool request fails. |

Three decisions mattered most. First, we kept the Planner and Builder paired by task but varied what their second calls saw. The testing experiment showed how copying an implementation explanation can copy a mistake into the test. Second, we gave the Builder a route back to the Planner. Earlier handoffs looked complete even when a default conflicted with the actual setter or an edit had no unique match. A scoped question and a source read are cheaper than rerunning Requirements. A fixture demonstrated the round trip; the final two cases do not establish that asking the Planner caused success. Third, the PR points to a frozen, checked commit. This let us change the harness and repeat review without silently changing the candidate.

GitHub accepts the autose:run label and /autose run comment from a maintainer. Model jobs share a concurrency group. The final review-posting job uses a short-lived Actions token with PR write access; no second personal account is required. A bot verdict does not satisfy a human branch-protection approval.

## 4. Which experiments changed the design?

Most changes came from reading a failed stage, changing one thing we thought mattered, and replaying its input. We also ran three small side-by-side comparisons. These used the 20B model at temperature zero, the same stage inputs and one attempt per condition per listed issue. The comparisons informed the next design; they do not measure a general model success rate.

| Stage comparison | Observation | Decision |
| --- | --- | --- |
| Requirements JSON object vs strict schema; cases 1, 2, 4 | Three provider-rejected proposals became structurally valid. Only case 2 passed quality. Cases 1 and 4 paused for clarification. | Keep strict proposal structure, independent audit, and a bounded text fallback validated locally. |
| Broad vs focused Design excerpts; case 3 | At the same 4,000 completion cap, broad input used 8,407 total tokens and returned an empty draft. Focused input used 6,820 and finished, but failed the mapping check and proposed None. | Narrow context where useful. Keep semantic and execution checks even when writing finishes. |
| Retained implementation answer vs patch-only testing context; case 3 | At 3,530 tokens the retained answer gave two candidate failures. At 3,458 the patch-only tests passed on the candidate and two errored on clean. A duplicate-table probe still fooled them. | Give the test writer the patch and public examples; require tests that distinguish multiple generated items. |

The three comparisons reported 30,415 tokens. A later validation on five original snapshots still saw provider rejections, including requests that had previously worked unchanged. The five-case controlled rerun with all final fixes was never performed.

The rate experiment answered a different question. Our Groq tier reported an 8,000-token minute budget shared by input and generated output. Initial jobs used different stage caps, including 3,000 and 4,000. Raising every output cap to 8,000 would leave no room for the prompt. The final controller uses smaller per-stage caps, estimates prompt size, reserves headroom, serializes model jobs and waits at least 60 seconds between calls within a paced job. A daily limit can still stop it.

In a saved 120B continuation, a Planner handoff used 6,459 total tokens. After a minute, test generation used 5,146 and the tests passed. This shows that two bounded requests can fit separate windows. It does not tell us what would have happened with no delay. The two final hosted verdicts used 2,522 and 3,345 tokens. No new model calls were needed to prepare this report.

## 5. What the tests could actually distinguish

For the table-class feature, we held the production patch fixed and changed what the test writer saw. Both requests included the accepted plan, the patch and a public example. One also included the implementation conversation. This setup let us examine the tests themselves on two revisions.

| Test or probe | Observed result | What we learned |
| --- | --- | --- |
| Retain the implementation answer | Two failures on the clean revision and two on the candidate. The clean suite passed after removing the generated tests. | The tests passed configuration to an already-created extension in a way Markdown ignored. The candidate had no opportunity to demonstrate the feature. |
| Omit the implementation answer | Candidate suite passed with 1,115 passes and 111 skips. The new tests exposed missing behavior on the clean revision. | The tests could distinguish these two revisions. We still needed to check which wrong outputs they would accept. |
| Reverse the CSS class order | The tests continued to pass. | An element can carry both requested classes in either order. The assertions tolerated this equivalent output. |
| Duplicate the first rendered table | The tests still passed when the output repeated the first table. | A count and a shared class can both be right while the second table’s contents are wrong. Distinct cell values give each table an observable identity. |

These observations explain why running a suite on the candidate alone was too weak a check. A clean-revision run answers whether the proposed test detects the missing feature. Altering the rendered output asks a different question: which implementation mistakes could survive the same assertions? This comparison used one frozen patch and one pair of generated test suites. It did not use the private acceptance checks.

## 6. How the two fixes reached review

| Failure we observed | Change and check |
| --- | --- |
| JSON validation error or truncated writer | Retry supported format errors once, validate the response locally and retain the original attempt. Split source inspection from final writing. |
| Lookup returned irrelevant paths or annotated edit text | Start with pinned source and public tests. Offer bounded filename/text search and read_file. Supply plain text for exact replacements; reject ambiguous matches. |
| Tilde repair ran out of prompt room | The next lookup left an estimated 887 tokens, below the 900-token floor. Switch to submission, retaining the editable source and latest lookup. The replay left 2,126 tokens and produced the two-line deletion. |
| Planner treated excluded cases as blockers | Explicitly compare each unresolved question with the issue's scope. Changing the audit alone still paused. A revised proposal followed by the audit passed. |
| Table option rejected an ordinary string | None and bool defaults send values through parseBoolValue. Use an empty string default for a text option. Show the shared setter to the agents, route this candidate-only error to Implementation and apply candidate-relative repairs to the verified prior edits. |
| CI failed after tests passed | Issue 2 lacked a changelog entry. Issue 3 had earlier formatting/spelling failures and a later W292 missing final newline. Generate the changelog from a trusted issue mapping, run lint/spelling with the suite, normalize the test module before freezing it, and recheck the exact head. |
| Review resume showed a green workflow with skipped jobs | GitHub propagated the skipped build ancestry. Check direct prerequisites and cancellation explicitly. Require publication and posted-review receipts to match the same issue and head. |
| Reviewer issued an invalid tool call after running tests | For a small patch, read bounded changed source hunks directly at the PR head. Supply them with the issue, full diff and isolated suite result to one independent verdict call. Keep lookup tools for larger changes. |

The original four responsibilities still make sense. The main change was where decisions happen. Code now handles the predictable parts: choosing a pin, reproducing a patch, checking CI, reading small changed hunks and posting a verdict. Models still decide what the issue means, propose code and tests, and explain whether the result meets the criteria.

When the earlier candidates were merged before hosted review, we created dedicated demo base branches at the original pins and reused the tested patches. The final PRs remained open for a human at verification. That operational recovery is part of the recorded result. It consumed no new Planner or Builder calls.

## 7. What the results support

| # | First hosted stop | Furthest demonstrated result |
| --- | --- | --- |
| 1 | Requirements: provider JSON rejection | Later proposal described the crash. Quality asked what value a valueless enabled HTML attribute should carry. Reproduction confirmed the exception; no accepted candidate. |
| 2 | Requirements: provider JSON rejection | Final PR 28 removed the seed regression. Five public and three private checks passed, hosted CI passed, and the bot posted APPROVE. |
| 3 | Design: writer exhausted its output cap | Final PR 29 implemented table classes. Four public and three private checks passed, hosted CI passed, and the bot posted APPROVE. |
| 4 | Requirements: provider JSON rejection | Later quality questions concerned option matching, IDs and nesting. Pinned TOC rejected the unknown option. No published implementation. |
| 5 | Requirements: material ambiguity | A later proposal captured a clearer error and nonzero exit. Design exhausted its lookup budget without reading a public CLI test. No published implementation. |

Case 2. Requirements specified both the heading ID and the TOC link. The Design found the forced substitution in slugify, but also suggested wiring already present in the extension. Builder searched for the separator, read the configuration and finally submitted just the deletion of the tilde-to-hyphen override. The same saved public tests produced two failures on the seed and five passes on the candidate. The tests were reused from guided work; a new autonomous test-writing call was not required. Local suite: 1,117 passed, 111 skipped. The hosted reviewer independently ran 1,215 passes and 13 skips, then approved commit 8220cfce9a13.

Case 3. Proposal and audit both repeated questions about empty values and unusual whitespace even though the issue excluded them. A new proposal resolved the scope and passed audit. The Design and first Builder submission chose None. Compilation passed. A rejected search call interrupted test writing, so we resumed that step. Actual rendering then failed. The model changed the default to an empty string, and the operator replayed its edit against the verified candidate. The revised tests exercised configured classes, omission, contents and raw HTML. After the newline fix, the checked patch passed 4 public tests, 3 private tests and the full suite (1,116 passes, 111 skips). The hosted reviewer ran 1,214 passes and 13 skips and approved commit 2d1b5c42050b.

evidence/model-calls.csv lists the retained per-call receipts, including rejected HTTP requests. evidence/issue-2 and issue-3 contain the actual plans, patches, tests, CI and review receipts. The local and hosted suites had different dependency sets and skip counts. Each pair of reported counts belongs to its own environment.

## 8. What we would do earlier

We would run one tiny candidate through publication, CI and review before tuning the models. A compiled patch told us nothing about whether GitHub would schedule CI, whether a changelog was required, or whether skipped jobs would suppress the review. A cheap fixture can test branch selection and routing; a real PR is needed to verify credentials, workflow triggers and posting permissions.

We would introduce saved handoffs before adding extra agents. LangGraph would have helped earlier with one specific need: a Builder that finds a contradiction should be able to ask one question, save the answer and continue. It is the bounded route and the checkpoint that save repeated work. An extra conversation every time would cost us a minute even when the answer is already in the source.

We would start test design by asking which wrong outputs still pass. An early table test accepted two copies of the first table. Asking for two distinguishable inputs and checking the resulting elements exposes that blind spot. We would also run formatting and spelling before freezing the patch and attach the runner output to the repair request.

We would record the decision before trying the variant: one hypothesis, what stays fixed, which gate decides success, and what counts as operator help. We changed the issue wording, model, context and tools during debugging. Those changes were reasonable engineering, but they make later comparisons difficult. We would reserve enough provider budget to repeat a few identical conditions on a different day.

Blinded reviewer check. Five seeded PRs used the same public table issue with the oracle held back. The recorded score was two correct verdicts, two incorrect and one unavailable. There was a false approval and a false request for changes. In a separate guided PR, the reviewer claimed the processor never received its configuration; the actual code passed it in extendMarkdown. Requiring source references and supplying the exact hunks gives the reviewer better evidence. The benchmark was not repeated after that fix. This is why the maintainer still decides what to merge.

Token accounting. The historical batch ledger accounts for 372,520 reported tokens. The two later final hosted review receipts add 5,867, giving a lower bound of 378,387 for those disjoint groups together. Further retries and stage replays also incurred usage. Unreported provider errors and incomplete exploratory records prevent an exact lifetime total. The call appendix overlaps some run ledgers and should not simply be added to this number.

## Appendix A. Limitations and threats to validity

Coverage. Five deliberately chosen Python-Markdown cases cannot measure performance on a random GitHub issue. Four descriptions were authored for the assignment, one was a two-line seeded regression and the two successful cases received the most attention. Larger multi-file changes, dependency upgrades and other languages remain untested.

Scope and model attribution. Case 1 shows a real failure and a real choice about serialized output. Case 4 involves preserving a heading while promoting its children. Case 5 leaves CLI messaging open. These stops combine ambiguity, model judgement, provider formatting and source retrieval. We cannot label the three cases beyond the model's ability. A useful next test would pin the issue wording, clarify just the acceptance contract, and repeat Requirements and Design with a fixed tool budget.

Internal validity. The accepted cases used resumed stages, guided edits or tests, and several harness revisions. A first Requirements experiment even preceded the architecture commit. The archived design and ADRs preserve the intended baseline, but the chronology was imperfect. We cannot infer that 120B, LangGraph or the one-minute wait independently caused either success. Both 20B and 120B proposed a bad None default. A matched repeated model comparison would be needed to quantify a model effect.

Measurement. Three private checks per case are useful probes, not complete specifications. A passing suite may omit a rare input. Public tests generated by the same model as the implementation can share its assumptions. The final reviewers used the same model family in a fresh context, so correlated mistakes are still possible. A bot comment records its verdict; formal approval and merge remain human actions.

Reproducibility and cost. The fork's application and candidate SHAs are pinned. Provider availability, token accounting, daily quota, tool syntax and GitHub service settings can still change. The final small-patch review shortcut has size and hunk limits. Larger patches take a different path that has less successful evidence. The workflow supports two review rounds, but applying requested changes and requesting another review can require a maintainer.

What we can claim. Two cases produced working fixes checked on both clean and candidate revisions, passed external CI and received an independent posted review. The initial five hosted attempts produced zero candidates. The final configuration was not run unattended from scratch on all five. Results for issues 1, 4 and 5 remain open. The strongest reproducible demonstration is to inspect the actual commits, run the saved examples and read the review on each matching head.

## Appendix B. What the independent reviewer caught

We gave the reviewer five draft PRs for the same public table-class request. The expected verdicts were recorded before the calls and withheld from the reviewer. Holding the brief fixed made it possible to see whether changing the patch changed the judgement.

| Draft | Recorded verdict | Evidence returned |
| --- | --- | --- |
| PR 8 and PR 9 | APPROVE | Each produced a posted finding. One approval across the benchmark accepted a defective patch. |
| PR 10 and PR 11 | REQUEST_CHANGES | Each produced a posted finding. One change request across the benchmark challenged an acceptable patch. |
| PR 12 | No verdict | The missing answer counted separately from a correct rejection. |

Only two initial attempts returned a verdict. A recovery attempt reduced the writer’s reasoning effort for the three incomplete cases while keeping the output cap fixed. Across the five drafts, four ultimately returned a verdict and two matched the oracle. The reviewer detected one of the three planted defects. The benchmark consumed 36,803 reported tokens, with one provider attempt of unknown cost.

### AI declaration · Student’s own words

Code writing part was completely handled by codex, I started with basline which gave errors and for that I analysed the error and suggested fix ofcourse took advice from codex as alternative in process, sometime Ideas provided sounded logical so accepted it. Some changed like choosing number model or deciding token cap and choosing time between calls. Like for issue identification, I mentioned type of issue and validated issue whereas Codex found such issues, I do not have any idea of markdown repo. For documentation part, we logged and pushed everything on github and later on, I provided structrue for report and it took stats and results to make report, videos and all. This part is clearly Human written
