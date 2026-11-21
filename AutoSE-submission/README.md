# AutoSE assignment submission

Two reviewed fixes came out of five issue studies. Both were completed by resuming saved stages. The original five issue-triggered runs are retained, including their failures. Start with the ten-page [report](report.pdf), then watch the [1 minute 52 second subtitled demo](demo.mp4). The [editable report](report.md) and [subtitle transcript](demo-guide.md) are included.

| Deliverable | Where to find it |
| --- | --- |
| Issue definitions, origins and observed outcomes | Report pp. 1 and 7, [five briefs](experiment/issues), [results CSV](results/results.csv) |
| Baseline and final architecture | [A2 architecture](architecture/ARCHITECTURE.md), [original component and sequence views](architecture/views), [final demo sequence](architecture/views/final-demo.md) |
| Design decisions and comparisons | Report pp. 2–6, [ADRs](architecture/decisions), [variant definitions](experiment/variants.md), [comparison results](experiment/comparisons.md) |
| Run evidence and independent review | [Run ledger](results/runs.md), [model call ledger](evidence/model-calls.csv), [evidence guide](evidence/README.md), [seeded reviewer benchmark](experiment/reviewer-results.md) |
| Hindsight, limitations and threats to validity | Report pp. 8–9 |
| Code and prompts | [Harness](workflow), [Actions workflows](.github/workflows), [A1 requirements skill](workflow/skills/requirements.md) |
| Repository URL only | [roll_number_a3_AutoSE.txt](roll_number_a3_AutoSE.txt) |

## Demo and setup

The fork is [AKGIIITH/markdown](https://github.com/AKGIIITH/markdown). The common application pin is `2c96e36ba4750cf18583d62e2fcecff49e077419`; the seeded TOC pin is `1e2b7f27aeefe70057025a1da0d10006dd11ad48`. The final release bases were `a3/demo-markdown-base` and `a3/demo-toc-base`. The deployed harness and the application are versioned separately.

To show the results without spending tokens, play the MP4 or run `bash demo-replay.sh` from this folder. The replay uses Bash, Python, git, tar, ripgrep and an authenticated GitHub CLI. It prints saved artifacts, runs actual Markdown conversions on exact revisions, and fetches jobs and reviews from GitHub. It can use local Git objects or download the pinned source. The provided folder contains the assignment harness and evidence. The full Python-Markdown application and git history are in the fork.

For a new live run, an authorized maintainer labels an open mapped issue `autose:run` or comments `/autose run`. From a checkout of the deployed fork, `bash workflow/demo.sh 2 3` triggers the cases serially. An existing eligible PR can resume with `/autose review`. Repeating a completed review is unnecessary for this demo. The fork uses repository secrets for Groq and release, a scoped Actions identity for posting, and human merge control. The budget confirmation and model-call limits are documented in the workflow. A provider-side budget or free tier is required for an actual spending cap.

## Models, tokens and AI use

Earlier experiments used Groq GPT-OSS 20B. The demonstrated configuration uses GPT-OSS 120B for Planner, Builder and Reviewer. Release is ordinary code. The historical batch ledger accounts for 372,520 tokens. The two final posted reviews used 5,867 additional tokens, one call per PR. Together those groups account for at least 378,387 tokens. Other exploratory calls, replays and unreported provider errors make the complete project total unknown.

Groq generated requirements, plans, edits, tests and review text. Codex helped implement and troubleshoot the controller, inspect GitHub logs, replay failed calls, compose model edits on their verified base, and prepare the report and subtitled evidence replay. The maintainer supplied the assignment scope and made deployment and merge decisions. On issue 2, saved public tests from guided work were reused. On issue 3, repairs were guided by runner diagnostics. The private tests remained outside agent prompts and outside this folder. The silent demo uses on-screen subtitles and actual output from read-only commands.

The [baseline AutoSE design](architecture/BASELINE.md) explains the four-job sketch separately from the A2 application guide. Public reproduction outputs for the three unresolved issues are in [remaining-issues-public-probes.json](evidence/remaining-issues-public-probes.json). These probes exercise the application pin and do not invoke a model.
