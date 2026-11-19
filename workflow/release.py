"""Prepare the exact tested candidate for a trusted fork release job."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from .baseline import Run, git
from .pilot import CASES_BY_BASE, ROOT
from .trigger import FORK


def inspect_test_run(issue, path):
    base, revision = CASES_BY_BASE[issue]
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    gate = json.loads((path / "gate.json").read_text(encoding="utf-8"))
    if (manifest["issue"], manifest["revision"], manifest["base_branch"], gate["outcome"]) != (
        issue, revision, base, "passed",
    ):
        raise ValueError("Testing evidence does not match the issue, base and revision")
    patch = (path / "diff.patch").read_bytes()
    patch_sha = hashlib.sha256(patch).hexdigest()
    if patch_sha != gate.get("candidate_patch_sha256"):
        raise ValueError("Candidate patch digest does not match the passed Testing gate")
    return base, revision, patch, patch_sha


def git_run(checkout, *args, **kwargs):
    return subprocess.run(["git", "-C", str(checkout), *args], check=True, capture_output=True, **kwargs)


def prepare_candidate(repo, revision, patch, issue, out):
    # The temporary Git index records the resulting tested tree. An ordinary
    # checkout from the caller is never edited.
    with tempfile.TemporaryDirectory(prefix="autose-release-") as tmp:
        checkout = Path(tmp)
        subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", "--no-checkout", str(repo), str(checkout)],
                       check=True, capture_output=True)
        git_run(checkout, "checkout", "--quiet", "--detach", revision)
        git_run(checkout, "apply", "--index", "-", input=patch)
        changes = git(checkout, "diff", "--cached", "--name-status", "--no-renames", "-z").decode().split("\0")
        for status, path in zip(changes[::2], changes[1::2]):
            if status == "A" and path == "tests/test_autose_acceptance.py":
                continue
            if status != "M" or not path.startswith("markdown/") or not path.endswith(".py"):
                raise ValueError(f"Candidate changes an unauthorized release path: {path}")
        modes = git(checkout, "ls-files", "--stage", "-z", "--", "markdown", "tests/test_autose_acceptance.py")
        if any(entry and not entry.startswith(b"100644 ") for entry in modes.split(b"\0")):
            raise ValueError("Release paths must be ordinary non-executable files")
        tree = git(checkout, "write-tree").decode().strip()
        base_tree = git(repo, "rev-parse", f"{revision}^{{tree}}").decode().strip()
        if tree == base_tree:
            raise ValueError("Frozen candidate has no changes from the application baseline")
        # A stable identity and parent make retries reproduce the same commit.
        date = git(repo, "show", "-s", "--format=%cI", revision).decode().strip()
        env = {**os.environ, "GIT_AUTHOR_NAME": "AutoSE", "GIT_AUTHOR_EMAIL": "autose@users.noreply.github.com",
               "GIT_COMMITTER_NAME": "AutoSE", "GIT_COMMITTER_EMAIL": "autose@users.noreply.github.com",
               "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
        commit = git_run(checkout, "commit-tree", tree, "-p", revision, "-m",
                         f"AutoSE candidate for issue #{issue}", env=env).stdout.decode().strip()
        ref = f"refs/heads/autose/issue-{issue}-{commit[:12]}"
        git_run(checkout, "update-ref", ref, commit)
        git_run(checkout, "bundle", "create", str(out), ref)
    return commit, tree, ref


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", type=int, choices=CASES_BY_BASE, required=True)
    parser.add_argument("--test-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--repo", type=Path, default=ROOT)
    args = parser.parse_args()
    os.umask(0o077)
    run = Run(args.out.resolve(), "release-preflight")
    run.save("manifest.json", dict(issue=args.issue, parent_run=str(args.test_run.resolve()), fork=FORK))
    try:
        base, revision, patch, patch_sha = inspect_test_run(args.issue, args.test_run)
        head, tree, ref = prepare_candidate(
            args.repo.resolve(), revision, patch, args.issue, run.path / "candidate.bundle",
        )
        run.save("candidate.json", dict(fork=FORK, base=base, revision=revision, head_sha=head,
                                        tree_sha=tree, ref=ref, candidate_patch_sha256=patch_sha))
        run.write("pr.md", f"# Issue {args.issue} release preflight\n\n"
                  f"Candidate `{head}` targets `{FORK}` on `{base}` from `{revision}`.\n"
                  "The patch digest matches the passed testing gate. This preflight made no GitHub writes.\n")
        outcome = "ready_to_publish"
    except (OSError, KeyError, ValueError, subprocess.SubprocessError) as exc:
        run.save("error.json", dict(type=type(exc).__name__, message=str(exc)))
        outcome = "release_preflight_failed"
    run.save("gate.json", dict(outcome=outcome))
    print(outcome)
    return 0 if outcome == "ready_to_publish" else 1


if __name__ == "__main__":
    raise SystemExit(main())
