# Final demo sequence

Read this alongside the original component view and ADRs. The original sequence describes an earlier pilot. This sequence describes the final delivery for issue 3.

| Step | Who handed what to whom | Observed result |
| --- | --- | --- |
| 1 | Maintainer comment → authorizer → requirements Planner and quality check | The hosted run paused on empty values and unusual whitespace. The user had excluded both. A new proposal and independent check passed. |
| 2 | Accepted specification and pinned architecture → Design writer | The plan linked the extension, its setter and existing public tests. Its proposed default still contained a semantic error. |
| 3 | Design and source excerpts → Builder → compile gate | The edit compiled. A lookup failed during test generation; test writing resumed with the existing implementation. |
| 4 | Runner on clean and candidate → repair → same runner | A runtime conversion to boolean exposed the None default. The repaired text option passed the public checks. |
| 5 | Frozen candidate → release script → PR and exact-head CI | A missing final newline surfaced in CI. The corrected candidate was republished against the pinned base as PR 29. |
| 6 | Maintainer review command → CI verification → fresh read-only Reviewer → bot poster | The suite ran in isolation. The final writer saw the issue, diff, changed source and suite counts. GitHub recorded APPROVE on 2d1b5c42050b. The PR stayed open. |

The review-only run intentionally skipped plan-build and release-preflight. Authorization, publication handoff verification, CI verification, model review and posting all succeeded. [Final run](https://github.com/AKGIIITH/markdown/actions/runs/44909670652) · [Posted review](https://github.com/AKGIIITH/markdown/pull/29#pullrequestreview-6005551412)
