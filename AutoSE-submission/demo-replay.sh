#!/usr/bin/env bash
# Read-only demo. Run from a checkout of the fork. Optional argument picks a chapter.
set -euo pipefail
dir=$(cd -- "$(dirname -- "$0")" && pwd)
repo=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null || true)
fork=AKGIIITH/markdown
show() {
    printf '$'; printf ' %s' "$@"; printf '\n'
    "$@"
}
sample() (
    pin=$1
    temp=$(mktemp -d)
    trap 'rm -rf -- "$temp"' EXIT
    if [[ -n "$repo" ]] && git -C "$repo" cat-file -e "$pin^{commit}" 2>/dev/null; then
        git -C "$repo" archive "$pin" | tar -x -C "$temp"
    else
        gh api "repos/$fork/tarball/$pin" | tar -xz --strip-components=1 -C "$temp"
    fi
    cd "$temp"
    printf 'Checkout %.12s\n' "$pin"
    if [[ $2 == toc ]]; then
        printf '%s\n' '# Exam Notes' | python3 -c 'import sys,markdown; from markdown.extensions.toc import TocExtension; print(markdown.markdown(sys.stdin.read(), extensions=[TocExtension(separator="~")]))'
    else
        python3 -c 'import markdown; print(markdown.markdown("| A | B |\n|---|---|\n| 1 | 2 |",extensions=["tables"],extension_configs={"tables":{"table_class":"report-table compact"}}))'
    fi
)
chapter() {
    case "$1" in
    issue) show gh issue view 2 -R "$fork" --json title,url --jq '.title, .url'
           printf '\nSaved accepted specification\n'; python3 - "$dir/evidence/issue-2/spec.md" <<'PY'
import pathlib,sys
print(pathlib.Path(sys.argv[1]).read_text().split('##')[0].strip())
PY
           ;;
    design) printf 'Saved design and verified production edit\n'
            rg -m 1 -o 'markdown/extensions/toc.py' "$dir/evidence/issue-2/design.md" | head -1
            cat "$dir/evidence/issue-2/production.diff.patch";;
    behavior) printf 'Render "# Exam Notes" with TocExtension(separator="~")\n\n'
              sample 1e2b7f27aeefe70057025a1da0d10006dd11ad48 toc
              sample 8220cfce9a13700b37ef0746d5b0bdb96e745493 toc;;
    tests) cat "$dir/evidence/issue-2/test_report.md" | sed -E 's/\[([^]]+)\]\([^)]+\)/\1/g';;
    table) printf 'Render a Markdown table with table_class="report-table compact"\n\n'; sample 2d1b5c42050b75c7851bbf660590f90fc647e748 table;;
    hosted) show gh run view 44909448352 -R "$fork" --json jobs --jq '.jobs[] | [.name,.conclusion] | @tsv';;
    reviews) for n in 28 29; do
             show gh api "repos/$fork/pulls/$n/reviews" --jq '.[] | select(.user.login=="github-actions[bot]") | .user.login, (.body | split("\n")[0]), .commit_id, .html_url'
             done;;
    results) printf 'Initial issue-triggered runs\n'; python3 - "$dir/results/results.csv" <<'PY'
import csv,sys
for row in csv.DictReader(open(sys.argv[1])):
    if row['mode']=='hosted_baseline':print('Issue '+row['case']+'   '+row['last_gate'])
print('\nLater guided deliveries: issues 2 and 3.')
print('No published fixes demonstrated for issues 1, 4 and 5.')
PY
            ;;
    *) return 2;;
    esac
}
if [[ $# == 0 ]]; then
    for c in issue design behavior tests table hosted reviews results; do chapter "$c"; done
else chapter "$1"; fi
