# Issue #3 with GPT-OSS 120B

The maintainer selected Groq GPT-OSS 120B for a deadline experiment on the
same fork, application pin, and public issue. The project listed 120B through
the Groq model endpoint. The original 20B baseline remains available. The
experiment kept the 3,000-token Requirements, lookup, and Implementation
caps, the 4,000-token Design writing and Testing caps, and four calls per
SDK Builder task.

| Attempt | Evidence |
| --- | --- |
| Fresh Issue #3 | Both calls finished normally and the quality check accepted all four criteria. It paused on raw HTML tables and explicit empty values. Usage was 3,383 tokens. |
| Clarified issue input | The maintainer excluded raw HTML and explicit empty values. The quality checker accepted all four criteria but paused on a new table-syntax question. Usage was 3,956 tokens. |
| Maintainer-approved Requirements | A separate receipt records the human approval of the unchanged proposal. LangGraph then routed it to live Design. |
| Design | Four tool calls found and read pinned source and public tests. The writer finished normally. Its table used bold numbers, so the checker rejected its four mappings. Usage was 19,446 tokens. Codex fixed the format checker and revalidated the original answer without altering the draft. The draft still proposed `None` for the string-valued option. |
| Builder and first test-writing attempt | Builder submitted and compiled a patch with the same `None` default. The test writer found and read the pinned test helper and public table examples. Groq rejected its final request with HTTP 413 before generation, reporting 8,291 requested tokens against an 8,000-token per-minute limit. This attempt reported 19,884 tokens plus one request of unreported usage. |
| Test-only retry | The 5,160-token response produced a complete test module. The clean and candidate revisions both recorded three errors from unsupported extension tuples and one failure from Markdown indented as code. |
| Test correction | Given public failures and the pinned API, the model corrected the argument shape. The clean revision's configured cases now raised `KeyError` for the missing feature, and the candidate raised `ValueError` from boolean coercion. The default case still shared an input-indentation failure. Usage was 5,244 tokens. |
| Production repair | The 7,386-token Builder response identified the empty-string default. The harness rejected it because its exact old text was in the previous candidate. Codex applied the model's exact replacement at that candidate and reconstructed the combined diff against the pinned base. The unchanged tests showed that the configuration errors disappeared and that indented input still produced zero tables. |
| Final test submission | The model submitted four tests using valid unindented inputs, including two distinct tables in one document. It used 4,880 tokens. Identical tests ran on both revisions. The clean revision recorded one pass and three errors, and the candidate passed all four. Its full public suite recorded 1,116 passes and 111 skips. |
| Release and private evaluation | Release preflight froze commit `fefdf03d1bc9d83fcda85a1b068ec08004dbf79f`. All three private checks passed separately on that exact commit. The trusted publisher opened [PR #15](https://github.com/AKGIIITH/markdown/pull/15). |

LangGraph now sequences the accepted artifact through Requirements, Design,
and Builder, and stops on a failed gate. Testing stays separate during live
runs. The SDK graph and the changelog handoff were verified with scripted
replays. The trusted Testing runner can add the project's required
changelog note before it tests and freezes the candidate.

Known model usage through Testing was 69,339 tokens, plus the rejected request with
unreported usage. 120B wrote the design, application edits, and public
tests. The maintainer supplied scope and accepted Requirements. Codex
repaired the Design validator, composed the model's candidate-relative
edit, and ran the harness. This was a guided Requirements and harness
recovery with a model-authored tested PR.

## GitHub CI recovery

GitHub passed the changelog check on the first PR head. Flake8 requested
two blank lines in the generated test module, and the spelling check
flagged `attr` in a docstring. Codex changed only those blank lines and the
docstring and verified that the executable syntax tree was identical.
The retested tree passed the full public gate with the same counts.
The first formatting revision passed flake8 and the spelling check found
the remaining occurrence in the same docstring. A second docstring-only
retest produced the exact tree now published at
`b9c9fdc213b61d4af1478b5c88a8c724d62227df`. The independent private
evaluation passed all three cases on this head. All earlier commits and
CI evidence remain in the PR history. GitHub CI passed on the exact
current head, with 13 successful checks and one skipped release-only check.

[Original checks](https://github.com/AKGIIITH/markdown/actions/runs/44810387807) ·
[First retest](https://github.com/AKGIIITH/markdown/actions/runs/44811083687) ·
[Current head checks](https://github.com/AKGIIITH/markdown/actions/runs/44811501466).

## Independent Review

The fresh review used only public PR data and pinned source, with no
GitHub write credential. The single inspection call requested a local
suite run. The isolated runner was unavailable. The model returned
`REQUEST_CHANGES` and routed to Implementation. Codex corrected the
parser to accept the model's bold labels and preserved the original text.
The Reviewer used 6,213 reported tokens.

The review incorrectly claimed the table processor received no
configuration and that CI did not run the tests. The verified head
stores the configuration in `TableProcessor.__init__` and passes it in
`TableExtension.extendMarkdown`. CI passed on the same head. The
[posted review comment](https://github.com/AKGIIITH/markdown/pull/15#pullrequestreview-5998959116)
contains the verbatim findings and a separate operator verification. The
record keeps `MERGE_READINESS_CHECK=CHANGES_REQUIRED` as the model verdict.
The PR remains open for a human decision.
