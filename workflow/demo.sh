#!/usr/bin/env bash
set -euo pipefail

repo=AKGIIITH/markdown
diagnose_run() (
    run_id=$1
    evidence=$(mktemp -d)
    trap 'rm -r -- "$evidence"' EXIT
    gh run download "$run_id" --repo "$repo" --name autose-model-evidence --dir "$evidence"
    python3 - "$evidence" <<'PYTHON'
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
for stages in sorted(root.rglob("stages.json")):
    records = json.loads(stages.read_text())
    for record in records:
        print(f"{record['stage']}: {record['gate']} ({record['seconds']:.1f}s)")
    if records and records[-1].get("artifact"):
        artifact = stages.parent / Path(records[-1]["artifact"]).name
        for name in ("error.json", "runner-error.json", "judgment.json", "return-to-stage.json"):
            path = artifact / name
            if path.is_file():
                data = json.loads(path.read_text())
                if name == "judgment.json":
                    data = data.get("blocking_ambiguities", [])
                print(f"{name}: {json.dumps(data, ensure_ascii=False)}")
PYTHON
)

if [[ "${1:-}" == --diagnose ]]; then
    if [[ $# != 2 || ! "$2" =~ ^[0-9]+$ ]]; then
        printf 'Usage: bash workflow/demo.sh --diagnose <Actions run ID>\n' >&2
        exit 2
    fi
    diagnose_run "$2"
    exit
fi

if [[ "${1:-}" == --clarify ]]; then
    if [[ $# != 3 || ! "$2" =~ ^[1-5]$ || ! -s "$3" ]]; then
        printf 'Usage: bash workflow/demo.sh --clarify <issue number 1–5> <nonempty clarification file>\n' >&2
        exit 2
    fi
    (
        body=$(mktemp)
        trap 'rm -f -- "$body"' EXIT
        gh issue view "$2" --repo "$repo" --json body --jq .body > "$body"
        printf '\n## Maintainer clarification\n\n' >> "$body"
        cat -- "$3" >> "$body"
        gh issue edit "$2" --repo "$repo" --body-file "$body"
    )
    exit
fi

if (( $# == 0 )); then
    set -- 2 3
fi

for issue in "$@"; do
    if [[ ! "$issue" =~ ^[1-5]$ ]]; then
        printf 'Usage: bash workflow/demo.sh [issue number 1–5 ...]\n' >&2
        exit 2
    fi
done

default_branch=$(gh api "repos/$repo" --jq '.default_branch')
if [[ "$default_branch" != main ]]; then
    printf 'AutoSE expects main as the default branch of %s. GitHub reports %s.\n' "$repo" "$default_branch" >&2
    exit 1
fi

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
for path in .github/workflows/autose.yml workflow/design.py; do
    if ! deployed=$(gh api "repos/$repo/contents/$path?ref=main" --jq '.sha'); then
        printf 'Could not verify %s on GitHub main. Check its deployment and your GitHub CLI access.\n' "$path" >&2
        exit 1
    fi
    expected=$(git hash-object "$repo_root/$path")
    if [[ "$deployed" != "$expected" ]]; then
        printf 'GitHub main has a different %s from this checkout. Deploy the current AutoSE changes before starting the demo.\n' "$path" >&2
        exit 1
    fi
done

workflow_state=$(gh api "repos/$repo/actions/workflows/autose.yml" --jq '.state')
if [[ "$workflow_state" != active ]]; then
    printf 'GitHub reports the AutoSE workflow state as %s. Check the workflow in the Actions tab.\n' "$workflow_state" >&2
    exit 1
fi

latest_run() {
    gh run list --repo "$repo" --workflow autose.yml --branch main --event issue_comment --limit 30 \
        --json databaseId,displayTitle \
        --jq "[.[] | select(.displayTitle == \"AutoSE #$1\") | .databaseId] | max // 0"
}

status=0
for issue in "$@"; do
    prior=$(latest_run "$issue")
    gh issue comment "$issue" --repo "$repo" --body '/autose run'
    run=0
    for ((poll = 0; poll < 30; poll++)); do
        run=$(latest_run "$issue")
        if (( run > prior )); then
            break
        fi
        sleep 5
    done
    if (( run <= prior )); then
        printf 'No run titled AutoSE #%s appeared within 150 seconds. Recent comment-triggered runs on main:\n' "$issue" >&2
        gh run list --repo "$repo" --workflow autose.yml --branch main --event issue_comment --limit 5 \
            --json displayTitle,status,conclusion,url >&2 || true
        status=1
        continue
    fi

    printf 'Issue #%s Actions run: https://github.com/%s/actions/runs/%s\n' "$issue" "$repo" "$run"
    if ! gh run watch "$run" --repo "$repo" --exit-status; then
        diagnose_run "$run" || true
        status=1
    fi
    out=$(mktemp -d "${TMPDIR:-/tmp}/autose-demo-${run}.XXXXXX")
    gh run download "$run" --repo "$repo" --dir "$out" \
        --pattern autose-publication --pattern autose-posted-review || {
        printf 'Could not download the publication or review artifacts. Inspect the run jobs above for failed or skipped gates.\n' >&2
        status=1
    }
    python3 - "$out" <<'PY'
import json
from pathlib import Path
import sys

directory = Path(sys.argv[1])
for name in ("pr.json", "posted-review.json"):
    for path in directory.rglob(name):
        result = json.loads(path.read_text(encoding="utf-8"))
        print(result["url"])
PY
done
exit "$status"
