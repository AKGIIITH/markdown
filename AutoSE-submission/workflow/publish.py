"""Publish an exact Release preflight candidate and verify its PR CI gate."""

import argparse
import json
import os
import re
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.parse import quote, urlencode

from .baseline import Run, git
from .github import API, GitHub
from .pilot import CASES_BY_BASE, ROOT
from .release import git_run
from .trigger import FORK


APP_INPUTS = ("markdown", "tests", "docs", "pyproject.toml", "tox.ini", "uv.lock", ".pyspelling.yml", ".spell-dict",
              ".github/workflows/tox.yml", ".github/workflows/changelog-enforcer.yml")
EXPECTED_CI_JOBS = {
    "test": ("py311", "py312", "py313", "py314", "py315", "pypy311", "pygments"),
    "lint": ("flake8", "pep517check", "checklinks", "checkspelling"),
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_target(repo, client, issue, candidate):
    base, revision = CASES_BY_BASE[issue]
    if (candidate["fork"], candidate["base"], candidate["revision"]) != (FORK, base, revision):
        raise ValueError("Release candidate refers to an unexpected fork, base or application revision")
    if candidate["ref"] != f"refs/heads/autose/issue-{issue}-{candidate['head_sha'][:12]}":
        raise ValueError("Release candidate has an unexpected branch ref")
    repo_info = client.request(API)
    if repo_info["full_name"] != FORK or repo_info["default_branch"] != "main":
        raise ValueError("Fork identity or default branch changed")
    base_sha = client.request(API + "/branches/" + quote(base, safe=""))["commit"]["sha"]
    git_run(repo, "merge-base", "--is-ancestor", revision, base_sha)
    if git(repo, "diff", "--name-only", revision, base_sha, "--", *APP_INPUTS):
        raise ValueError("Application or CI inputs on the release base differ from the tested baseline")
    issue_data = client.request(f"{API}/issues/{issue}")
    if issue_data["state"] != "open" or "pull_request" in issue_data:
        raise ValueError("The mapped GitHub issue must still be open")
    return base_sha, issue_data


def push_bundle(path, candidate, client, run):
    ref = candidate["ref"]
    branch = ref.removeprefix("refs/heads/")
    branch_path = API + "/git/ref/" + quote(ref.removeprefix("refs/"), safe="/")
    existing = client.request(branch_path, missing=True)
    if existing is not None and existing["object"]["sha"] != candidate["head_sha"]:
        raise ValueError("Existing candidate branch points to a different commit")
    with tempfile.TemporaryDirectory(prefix="autose-publish-") as tmp:
        root = Path(tmp)
        checkout = root / "bundle"
        subprocess.run(["git", "clone", "--quiet", "--no-checkout", "--branch", branch, str(path), str(checkout)],
                       check=True, capture_output=True)
        evidence = git(checkout, "rev-parse", "HEAD", "HEAD^{tree}", "HEAD^").decode().splitlines()
        if evidence != [candidate["head_sha"], candidate["tree_sha"], candidate["revision"]]:
            raise ValueError("Bundle head, tree or parent differs from Release preflight")
        if existing is None:
            askpass = root / "askpass"
            askpass.write_text("#!/bin/sh\ncase \"$1\" in\n"
                               '*Username*) printf "%s\\n" x-access-token ;;\n'
                               '*Password*) printf "%s\\n" "$AUTOSE_PUSH_TOKEN" ;;\n'
                               "*) exit 1 ;;\nesac\n", encoding="utf-8")
            askpass.chmod(0o700)
            env = {**os.environ, "GIT_ASKPASS": str(askpass), "GIT_TERMINAL_PROMPT": "0",
                   "AUTOSE_PUSH_TOKEN": client.token}
            push = subprocess.run(
                ["git", "-c", "credential.helper=", "push", "--porcelain",
                 f"https://github.com/{FORK}.git", f"{candidate['head_sha']}:{ref}"],
                cwd=checkout, env=env, capture_output=True, text=True, timeout=120,
            )
            run.write("push.log", push.stdout + push.stderr)
            if push.returncode:
                raise ValueError(f"Candidate push failed with exit code {push.returncode}")
    remote = client.request(branch_path)
    if remote["object"]["sha"] != candidate["head_sha"]:
        raise ValueError("Remote branch does not match the tested candidate")
    return branch


def verify_pr(pr, record):
    if (pr["state"], pr["head"]["sha"], pr["base"]["ref"], pr["base"]["sha"]) != (
        "open", record["head_sha"], record["base"], record["base_sha"],
    ) or pr["base"]["repo"]["full_name"] != FORK or pr["head"]["repo"]["full_name"] != FORK:
        raise ValueError("PR state, fork, base or head changed")


def publish(args, run, client):
    preflight = args.preflight.resolve()
    manifest = read_json(preflight / "manifest.json")
    if manifest["issue"] != args.issue or read_json(preflight / "gate.json")["outcome"] != "ready_to_publish":
        raise ValueError("Release preflight did not pass for this issue")
    candidate = read_json(preflight / "candidate.json")
    base_sha, issue = verify_target(args.repo, client, args.issue, candidate)
    branch = push_bundle(preflight / "candidate.bundle", candidate, client, run)
    query = urlencode(dict(state="all", base=candidate["base"], head=f"{FORK.split('/')[0]}:{branch}"))
    existing = client.request(API + "/pulls?" + query)
    if len(existing) > 1 or (existing and existing[0]["state"] != "open"):
        raise ValueError("A human has already disposed of this candidate PR")
    if existing:
        pr = existing[0]
    else:
        pr = client.request(API + "/pulls", dict(
            title=f"AutoSE issue #{args.issue}: {issue['title']}"[:240],
            base=candidate["base"], head=branch,
            body=(f"Implements #{args.issue}. The public test suite passed before publication.\n\n"
                  f"Tested revision: `{candidate['head_sha']}`.\n"
                  "The maintainer makes the final merge decision."),
        ))
    record = dict(issue=args.issue, fork=FORK, number=pr["number"], url=pr["html_url"],
                  head_sha=candidate["head_sha"], branch=branch, base=candidate["base"], base_sha=base_sha)
    # Keep the PR reference even if a concurrent edit makes verification fail.
    run.save("pr.json", record)
    latest = client.request(f"{API}/pulls/{pr['number']}")
    verify_pr(latest, record)
    run.write("pr.md", f"# Issue {args.issue} release\n\n[PR #{pr['number']}]({record['url']})\n\n"
              f"Published head `{record['head_sha']}` on base `{record['base']}`. CI verification pending.\n")
    return "published"


def review_identity(client):
    if os.getenv("AUTOSE_ACTIONS_REVIEW") == "true":
        return "github-actions[bot]"
    return client.request("/user")["login"]


def requests_changes(review):
    if review["state"] == "COMMENTED":
        return (review.get("body") or "").startswith("AutoSE independent verdict: REQUEST_CHANGES\n")
    return review["state"] == "CHANGES_REQUESTED"


def prepare_rereview(args, run, client):
    endpoint = f"{API}/pulls/{args.pr}"
    pr = client.request(endpoint)
    branch = pr["head"]["ref"]
    match = re.fullmatch(r"autose/issue-([1-5])-[a-f0-9]{12}", branch)
    if not match:
        raise ValueError("Review requires a published AutoSE PR")
    issue = int(match[1])
    base, revision = CASES_BY_BASE[issue]
    record = dict(issue=issue, fork=FORK, number=args.pr, url=pr["html_url"],
                  head_sha=pr["head"]["sha"], branch=branch, base=base, base_sha=pr["base"]["sha"])
    verify_pr(pr, record)
    git_run(args.repo, "merge-base", "--is-ancestor", revision, record["base_sha"])
    if git(args.repo, "diff", "--name-only", revision, record["base_sha"], "--", *APP_INPUTS):
        raise ValueError("Application or CI inputs on the release base differ from the tested baseline")

    reviewer = review_identity(client)
    reviews = []
    for page in range(1, 11):
        rows = client.request(f"{endpoint}/reviews?per_page=100&page={page}")
        reviews.extend(row for row in rows if row["user"]["login"] == reviewer)
        if len(rows) < 100:
            break
    else:
        raise ValueError("Could not verify prior review rounds")
    markers = {round_number: f"<!-- autose-review:{issue}:round-{round_number} -->"
               for round_number in (1, 2)}
    prior = [row for row in reviews if (row.get("body") or "").endswith(markers[1])]
    if any((row.get("body") or "").endswith(markers[2]) for row in reviews):
        raise ValueError("The second review round has already been used")
    if prior:
        if (len(prior) != 1 or not requests_changes(prior[0])
                or prior[0]["commit_id"] == record["head_sha"]):
            raise ValueError("Round 2 requires changes on the PR after an authenticated round 1 request")
        round_number = 2
    else:
        # CI fixes can follow publication. Require the original Release commit
        # on this branch and verify its pinned parent before reviewing a descendant.
        original = branch.rsplit("-", 1)[1]
        if not record["head_sha"].startswith(original):
            anchor = client.request(f"{API}/commits/{original}")
            if [p["sha"] for p in anchor["parents"]] != [revision]:
                raise ValueError("Candidate branch does not identify a commit on the pinned revision")
            comparison = client.request(f"{API}/compare/{anchor['sha']}...{record['head_sha']}")
            if comparison["status"] != "ahead":
                raise ValueError("Repaired candidate does not descend from its published commit")
        round_number = 1
    verify_pr(client.request(endpoint), record)
    run.save("pr.json", record)
    run.write("pr.md", f"# Review round {round_number}\n\n[PR #{args.pr}]({record['url']})\n\n"
              f"Recheck CI on the current head `{record['head_sha']}`.\n")
    print(f"issue={issue}")
    print(f"round={round_number}")
    return "published"


def successful_matrix(jobs):
    completed = set()
    for job in jobs:
        if job["status"] != "completed" or job["conclusion"] != "success":
            continue
        group, separator, details = job["name"].removesuffix(")").partition(" (")
        if separator:
            completed.add((group, details.split(",", 1)[0].strip()))
    return all((group, item) in completed for group, items in EXPECTED_CI_JOBS.items() for item in items)


def ci_snapshot(record, client):
    endpoint = f"{API}/pulls/{record['number']}"
    pr = client.request(endpoint)
    verify_pr(pr, record)
    heads = {record["head_sha"]}
    if pr.get("merge_commit_sha"):
        heads.add(pr["merge_commit_sha"])
    runs = {}
    checks = {}
    for head in sorted(heads):
        params = urlencode(dict(event="pull_request", head_sha=head, per_page=100))
        data = client.request(f"{API}/actions/workflows/tox.yml/runs?{params}")
        for row in data["workflow_runs"]:
            if row["head_sha"] in heads and row["head_branch"] == record["branch"]:
                runs[row["id"]] = row
        data = client.request(f"{API}/commits/{head}/check-runs?per_page=100")
        checks.update({row["id"]: {key: row[key] for key in ("name", "status", "conclusion", "html_url")}
                       for row in data["check_runs"]})
    latest = client.request(endpoint)
    verify_pr(latest, record)
    if latest.get("merge_commit_sha") != pr.get("merge_commit_sha"):
        raise ValueError("PR merge revision changed while checking CI")
    run = max(runs.values(), key=lambda row: row["id"], default=None)
    evidence = dict(head_sha=record["head_sha"], merge_sha=pr.get("merge_commit_sha"),
                    checks=list(checks.values()), workflow=None)
    if run:
        jobs = client.request(f"{API}/actions/runs/{run['id']}/jobs?filter=latest&per_page=100")["jobs"]
        evidence["workflow"] = {key: run[key] for key in ("id", "head_sha", "html_url", "status", "conclusion")}
        evidence["workflow"]["jobs"] = [{key: job[key] for key in ("name", "status", "conclusion", "html_url")}
                                        for job in jobs]
        verify_pr(client.request(endpoint), record)
        if run["status"] == "completed":
            if run["conclusion"] != "success" or not successful_matrix(jobs):
                return "ci_failed", evidence
            if any(check["conclusion"] in ("failure", "cancelled", "timed_out", "action_required")
                   for check in checks.values()):
                return "ci_failed", evidence
            changelog_ok = any(check["name"] == "check-for-entry" and check["conclusion"] == "success"
                               for check in checks.values())
            if changelog_ok and all(check["status"] == "completed" for check in checks.values()):
                return "passed", evidence
    return "ci_pending", evidence


def verify_ci(args, run, client):
    record = read_json(args.publication / "pr.json")
    if record["issue"] != args.issue or record["fork"] != FORK:
        raise ValueError("Publication evidence belongs to a different issue or fork")
    deadline = time.monotonic() + args.timeout
    poll = 0
    while True:
        poll += 1
        outcome, evidence = ci_snapshot(record, client)
        run.save(f"ci-poll-{poll}.json", evidence)
        run.save("ci.json", evidence)
        run.event("ci_poll", outcome=outcome)
        if outcome != "ci_pending" or time.monotonic() >= deadline:
            break
        time.sleep(min(15, max(0, deadline - time.monotonic())))
    if outcome == "ci_pending":
        outcome = "ci_timed_out" if evidence["workflow"] else "ci_no_run"
    run.save("pr.json", record)
    workflow = evidence["workflow"]
    run.write("pr.md", f"# Issue {args.issue} release\n\n[PR #{record['number']}]({record['url']})\n\n"
              f"Verified head `{record['head_sha']}`. CI status `{outcome}`.\n"
              + (f"[CI run]({workflow['html_url']})\n" if workflow else "GitHub returned no matching CI run.\n"))
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", type=int, choices=CASES_BY_BASE)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("open").add_argument("--preflight", type=Path, required=True)
    rereview = commands.add_parser("rereview")
    rereview.add_argument("--pr", type=int, required=True)
    ci = commands.add_parser("ci")
    ci.add_argument("--publication", type=Path, required=True)
    ci.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    token = os.getenv("AUTOSE_GITHUB_TOKEN")
    if not token:
        parser.error("AUTOSE_GITHUB_TOKEN is required")
    if args.command != "rereview" and args.issue is None:
        parser.error("--issue is required for publication and CI verification")
    if args.command == "rereview" and args.pr < 1:
        parser.error("--pr must be positive")
    if args.command == "ci" and args.timeout < 0:
        parser.error("CI timeout cannot be negative")
    os.umask(0o077)
    run = Run(args.out.resolve(), "ci-verification" if args.command == "ci" else "publication")
    run.secret = token
    run.save("manifest.json", dict(issue=args.issue, fork=FORK, mode=args.command))
    try:
        client = GitHub(token)
        handlers = {"open": publish, "ci": verify_ci, "rereview": prepare_rereview}
        outcome = handlers[args.command](args, run, client)
    except (OSError, KeyError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        run.save("error.json", dict(type=type(exc).__name__, message=str(exc)))
        if not (run.path / "pr.md").exists():
            run.write("pr.md", f"# Release gate failed\n\n{type(exc).__name__}: {exc}\n")
        outcome = "ci_verification_failed" if args.command == "ci" else "publication_failed"
    run.save("gate.json", dict(outcome=outcome))
    print(outcome)
    return 0 if outcome in ("published", "passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
