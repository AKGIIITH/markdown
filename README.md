# AutoSE assignment submission

[Final report](report.pdf) · [Demo video](AutoSE-submission/demo.mp4) · [Run and review evidence](AutoSE-submission/results/runs.md) · [Submission guide and reproducible workflow](AutoSE-submission/README.md)

[Python-Markdown][]
===================

[![Build Status][build-button]][build]
[![Coverage Status][codecov-button]][codecov]
[![Latest Version][mdversion-button]][md-pypi]
[![Python Versions][pyversion-button]][md-pypi]
[![BSD License][bsdlicense-button]][bsdlicense]
[![Code of Conduct][codeofconduct-button]][Code of Conduct]

[build-button]: https://github.com/Python-Markdown/markdown/actions/workflows/tox.yml/badge.svg
[build]: https://github.com/Python-Markdown/markdown/actions/workflows/tox.yml
[codecov-button]: https://codecov.io/gh/Python-Markdown/markdown/branch/master/graph/badge.svg
[codecov]: https://codecov.io/gh/Python-Markdown/markdown
[mdversion-button]: https://img.shields.io/pypi/v/Markdown.svg
[md-pypi]: https://pypi.org/project/Markdown/
[pyversion-button]: https://img.shields.io/pypi/pyversions/Markdown.svg
[bsdlicense-button]: https://img.shields.io/badge/license-BSD-yellow.svg
[bsdlicense]: https://opensource.org/licenses/BSD-3-Clause
[codeofconduct-button]: https://img.shields.io/badge/code%20of%20conduct-contributor%20covenant-green.svg?style=flat-square
[Code of Conduct]: https://github.com/Python-Markdown/markdown/blob/master/CODE_OF_CONDUCT.md

This is a Python implementation of John Gruber's [Markdown][].
It is almost completely compliant with the reference implementation,
though there are a few known issues. See [Features][] for information
on what exactly is supported and what is not. Additional features are
supported by the [Available Extensions][].

[Python-Markdown]: https://Python-Markdown.github.io/
[Markdown]: https://daringfireball.net/projects/markdown/
[Features]: https://Python-Markdown.github.io#Features
[Available Extensions]: https://Python-Markdown.github.io/extensions

Documentation
-------------

```bash
pip install markdown
```
```python
import markdown
html = markdown.markdown(your_text_string)
```

For more advanced [installation] and [usage] documentation, see the `docs/` directory
of the distribution or the project website at <https://Python-Markdown.github.io/>.

[installation]: https://python-markdown.github.io/install/
[usage]: https://python-markdown.github.io/reference/

See the change log at <https://python-markdown.github.io/changelog/>.

Assignment workflow
-------------------

This [fork](https://github.com/AKGIIITH/markdown) uses application commit
`2c96e36ba4750cf18583d62e2fcecff49e077419`. Issue 2 uses the seeded
`a3/bug02-seed` branch at `1e2b7f27aeefe70057025a1da0d10006dd11ad48`.

### Terminal demo

With the workflow deployed on the default branch, sign in to the GitHub CLI
as a maintainer and run the two open experiment issues in order.

```bash
gh auth status
bash workflow/demo.sh 2 3
```

The script comments `/autose run`, watches each Actions run, and reads the PR
and review links from that run's artifacts. The `autose:run` label is also
supported. Allow a minute between model calls. The recording can cut the
waiting time and show the issue, gate artifacts, CI, independent review and
open PR. The existing [video](experiment/demo.mp4) shows the recorded evidence with narration.

### Repository setup

- Deploy the workflow and harness through a maintainer PR to protected `main`.
  Keep the pinned application and its CI inputs intact on the experiment bases.
- Set `GROQ_API_KEY`, `AUTOSE_RELEASE_TOKEN` and
  `AUTOSE_REVIEW_POST_TOKEN` as GitHub Actions secrets. The release identity
  needs branch and PR write access. Use a separate identity for posting reviews.
- Set `AUTOSE_PROVIDER_BUDGET` to the recorded provider budget and enable
  `AUTOSE_ENABLE_PUBLISH` and `AUTOSE_ENABLE_REVIEW` with the value `true`.
  Use a free provider account or configure a provider-side spending cap.
  The production and review jobs also limit their request counts.
- On a first-round change request, read the return-stage artifact, apply the
  fix on the same PR branch, then comment `/autose review` on the PR. The
  workflow verifies the changed head and CI before a fresh second review.
  A maintainer makes the final merge or close decision.

### Models and evidence

The hosted configuration uses `openai/gpt-oss-120b` for the Planner, Builder
and Reviewer. Earlier comparison runs used `openai/gpt-oss-20b`. The Planner
handles Requirements and Design. The Builder can ask the Planner a scoped
question through `LangGraph` and writes the patch and public tests. The
Reviewer starts with the issue, exact PR diff and source. Release is scripted.

The [timing and token ledger](results/runs.md) records **372,520 reported
tokens** in the enumerated batches. Provider errors and exploratory calls
without records can leave usage unknown. The new local replays used zero model
tokens.
The [report](report.pdf) and [experiment ledger](experiment/README.md)
distinguish recorded hosted runs, guided pull requests, and local replay.

`Codex` helped implement the harness and gates, analyze provider and CI logs,
write the report and demo instructions, and mechanically apply or repair
guided outputs. The maintainer supplied the assignment decisions and scope
clarifications. The guided evidence records the operator's public test and
formatting corrections, and explicitly identifies the review finding that
the operator could disprove.

Support
-------

You may report bugs, ask for help, and discuss various other issues on the [bug tracker][].

[bug tracker]: https://github.com/Python-Markdown/markdown/issues

Code of Conduct
---------------

Everyone interacting in the Python-Markdown project's code bases, issue trackers,
and mailing lists is expected to follow the [Code of Conduct].
