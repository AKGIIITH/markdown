# Demo chapters and subtitles

The silent video shows captured terminal output and saved handoffs. Run `bash demo-replay.sh` to repeat the commands.

## 0:00 · What should a heading link do?

0:00 — The user configured a tilde, but the heading ID still contained a hyphen.

0:07 — The accepted requirement covers both the heading ID and the link pointing to it.

## 0:14 · The cause was two lines in slugify

0:14 — The Planner found where the extension changed a tilde back to a hyphen.

0:21 — The Builder deleted those two lines. The remaining code already handled the separator.

## 0:28 · Same heading, same option, different result

0:28 — On the seeded revision, “Exam Notes” becomes exam-notes.

0:35 — On the reviewed candidate, the same input becomes exam~notes.

## 0:42 · Run the same tests on both revisions

0:42 — Two public tests fail on the original seed. All five pass after the fix.

0:49 — The candidate also passes the full local suite: 1,117 passes and 111 skips.

## 0:56 · A second fix: CSS classes on generated tables

0:56 — A None default made the extension try to read a CSS class as a boolean.

1:03 — With an empty string default, the table gets both classes and keeps its cell values.

## 1:10 · Resume review at the tested commit

1:10 — The candidate was already built and published, so this run skipped those jobs.

1:17 — GitHub verified CI, ran the independent reviewer and posted its verdict.

## 1:24 · Verify who posted each verdict

1:24 — The Actions bot posted APPROVE on the exact heading-fix commit in PR #28.

1:31 — It also approved the table fix in PR #29. The maintainer decides whether to merge.

## 1:38 · What happened across all five issues?

1:38 — These are the original five attempts. None reached a published candidate.

1:45 — After guided repairs, issues 2 and 3 reached review. Issues 1, 4 and 5 remain unresolved.
