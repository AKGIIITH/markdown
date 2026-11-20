# Blinded Reviewer results

The same public Issue #3 was used for five draft PRs. Oracle expectations were recorded before model calls and kept outside the prompts.
The benchmark measures review independently of the workflow’s CI gate.

| PR | Model verdict | Merge readiness check | Posted findings |
| --- | --- | --- | --- |
| [#8](https://github.com/AKGIIITH/markdown/pull/8) | APPROVE | `READY_FOR_HUMAN` | [Review comment](https://github.com/AKGIIITH/markdown/pull/8#pullrequestreview-5997230718) |
| [#9](https://github.com/AKGIIITH/markdown/pull/9) | APPROVE | `READY_FOR_HUMAN` | [Review comment](https://github.com/AKGIIITH/markdown/pull/9#pullrequestreview-5997231514) |
| [#10](https://github.com/AKGIIITH/markdown/pull/10) | REQUEST_CHANGES | `CHANGES_REQUIRED` | [Review comment](https://github.com/AKGIIITH/markdown/pull/10#pullrequestreview-5997232164) |
| [#11](https://github.com/AKGIIITH/markdown/pull/11) | REQUEST_CHANGES | `CHANGES_REQUIRED` | [Review comment](https://github.com/AKGIIITH/markdown/pull/11#pullrequestreview-5997232817) |
| [#12](https://github.com/AKGIIITH/markdown/pull/12) | Unavailable | `NO_VERDICT` | Unavailable |

Across 5 PRs there were 2 correct verdicts, 2 incorrect verdicts and 1 unavailable.
The Reviewer detected 1 of the three planted defects, made 1 false approval and 1 false change request.
Two initial attempts produced a verdict. A writer-only recovery reduced reasoning effort on the three incomplete cases at the same output cap.
The four actual findings were posted as review comments because the posting account opened the drafts. All draft PRs remain open.

Known usage was 36,803 tokens, with 1 provider attempt unreported.
