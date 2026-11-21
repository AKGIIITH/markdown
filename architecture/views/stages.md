# Workflow stages and Issue #3 pilot

| Stage | Owner | Artifact | Gate |
| --- | --- | --- | --- |
| Requirements | Planner and independent quality check | `spec.md`, structured proposal and judgment | Valid contract, grounded and observable criteria. A material ambiguity pauses for the maintainer. |
| Design | Planner | `design.md` | The plan identifies the pinned source, edit locations, and one public test per criterion. |
| Implementation | Builder | Production `diff.patch` and build log | The patch applies to the pinned application and builds. |
| Testing | Builder and runner | Public tests, final `diff.patch`, `test_report.md` | The same tests detect the issue on clean source and pass on the candidate. The suite passes. Failures route to the responsible stage. |
| Release | Trusted script | `pr.md`, PR URL, SHA and CI records | The published PR head matches the tested revision and expected CI checks pass. |
| Review | Independent Reviewer | `review.md` and posted review | The reviewer sees the issue, diff and current source. Requested changes route back. Two rounds maximum, with merge left to the maintainer. |

The application revision is selected independently of the harness. Issue #2
uses `a3/bug02-seed` at `1e2b7f2`. The other four issues use `main` at
`2c96e36`. Private tests evaluate a frozen result separately.

## Tools and execution

| Role | Access |
| --- | --- |
| Planner | Design can call `list_files`, `find_files`, `search_text` and `read_file` on the pinned public tree. Requirements and final Design writing are text calls. |
| Builder | Receives bounded excerpts and an editable path list. Proposes exact replacements and a Python test module. Trusted runners apply edits, compile, and execute the public tests against the clean and candidate revisions. |
| Release | A trusted script verifies the base and tested head, pushes the candidate, opens or reuses the PR, and checks GitHub CI. |
| Reviewer | Can use the pinned lookup tools and request `run_public_suite` in an isolated runner. A separate job posts the verdict. |

Planner, Builder and Reviewer use GPT-OSS 120B in the demo configuration.
Release is scripted. The hosted controller dispatches one repair from public
test or source lint evidence. For review changes, the workflow records the
stage to revise and accepts a second review after a maintainer updates the
same PR. The [later observed PR 15 sequence](sequence.md) includes exact-head
CI and posted review.

## Observed Issue #3 sequence

```mermaid
sequenceDiagram
    participant O as Pilot operator
    participant P as Groq Planner
    participant B as Groq Builder
    participant T as Local test runner
    participant G as Fork GitHub API
    O->>P: Issue and A1 skill
    P-->>O: Missing required field at 1,800-token limit
    O->>P: Revised Requirements and Design requests
    P-->>O: Specification and design
    O->>B: Corrected handoff and pinned tables source
    B-->>O: Production patch
    O->>T: Compile pinned source with patch
    T-->>O: Compilation passes
    O->>B: Public test request
    B-->>O: JSON validation failures, then truncated Python
    O->>B: Plain Python with 4,000-token limit
    B-->>O: Complete public tests
    O->>T: Original tests, then corrected distinct-table assertions
    T-->>O: Clean errors as expected; candidate tests and suite pass
    O->>G: Publish tested commit and open PR 6
    G-->>O: Exact head confirmed; no CI run registered
```

The first Requirements pilot preceded the architecture commit. The operator
selected source excerpts, corrected the Design handoff, and strengthened the
generated test assertions after measuring a duplicate-table blind spot. This
was a manually guided pilot. The autonomous requirements-quality policy in
ADR-003 came later and has been exercised with simulated judgments.

The Issue #3 candidate had three passing public tests and 1,115 passing suite
tests, with 111 skips. All three separate private tests passed. Known model
usage was 33,319 tokens, with unreported usage on earlier errors. The
[fork PR](https://github.com/AKGIIITH/markdown/pull/6) remains open on head
`955e49825259c6611c4c48d2d257f486ca8d0a41`. The release CI gate and independent
review are pending.
