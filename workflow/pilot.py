"""Run the local application gates against a candidate patch."""

import argparse
import hashlib
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import time

if __package__:
    from .baseline import CASES, SEED, Run, git
else:
    from baseline import CASES, SEED, Run, git


ROOT = Path(__file__).resolve().parents[1]
CASES_BY_BASE = {issue: ("a3/bug02-seed" if row[0] == SEED else "main", row[0])
                 for issue, row in CASES.items()}
COUNTS = re.compile(r"^Ran (\d+) tests? in ", re.MULTILINE)
PUBLIC_DIRS = ("markdown", "tests", "docs")
PUBLIC_CONFIG = ("pyproject.toml", "tox.ini", "README.md")


def application_file(repo, revision, path):
    """Read one pinned application file using a repository-relative path."""
    if Path(path).as_posix() != path or ".." in Path(path).parts:
        raise ValueError(f"Expected a normalized repository path: {path}")
    if not path.startswith(tuple(directory + "/" for directory in PUBLIC_DIRS)) and path not in PUBLIC_CONFIG:
        raise ValueError(f"Path outside the application and public tests: {path}")
    return git(repo, "show", f"{revision}:{path}")


def export(repo, revision, destination):
    blob = git(repo, "archive", revision)
    with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
        archive.extractall(destination, filter="data")


def test_counts(output):
    match = COUNTS.search(output)
    if match is None:
        return None
    tests = int(match[1])
    skips = len(re.findall(r" \.\.\. skipped ", output))
    failures = len(re.findall(r"^FAIL: ", output, re.MULTILINE))
    errors = len(re.findall(r"^ERROR: ", output, re.MULTILINE))
    expected_failures = len(re.findall(r" \.\.\. expected failure$", output, re.MULTILINE))
    unexpected_successes = len(re.findall(r" \.\.\. unexpected success$", output, re.MULTILINE))
    return dict(
        tests=tests,
        passed=tests - skips - failures - errors - expected_failures - unexpected_successes,
        skipped=skips,
        failures=failures,
        errors=errors,
        expected_failures=expected_failures,
        unexpected_successes=unexpected_successes,
    )


def execute(run, name, argv, checkout, home, stdin=None):
    env = {
        "HOME": str(home),
        "PATH": os.defpath,
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CEILING_DIRECTORIES": str(checkout.parent),
    }
    run.event("command_start", check=name, command=argv, checkout=str(checkout))
    start = time.monotonic()
    try:
        process = subprocess.run(
            argv, cwd=checkout, env=env, input=stdin,
            capture_output=True, timeout=300, check=False,
        )
        code, stdout, stderr = process.returncode, process.stdout, process.stderr
    except subprocess.TimeoutExpired as exc:
        code, stdout, stderr = None, exc.stdout or b"", exc.stderr or b""

    stdout, stderr = (stream.decode("utf-8", errors="replace") for stream in (stdout, stderr))
    run.write(f"{name}.stdout.log", stdout)
    run.write(f"{name}.stderr.log", stderr)
    result = dict(command=argv, checkout=str(checkout), exit_code=code,
                  seconds=round(time.monotonic() - start, 3), counts=test_counts(stderr))
    run.save(f"{name}.json", result)
    run.event("command_end", check=name, exit_code=code)
    return result


def verify_import(run, side, checkout, home):
    verify = (
        "import pathlib, sys, markdown; "
        "path = pathlib.Path(markdown.__file__).resolve(); "
        "print(sys.version, sys.executable, path, sep='\\n'); "
        "assert path == pathlib.Path.cwd() / 'markdown/__init__.py'"
    )
    return execute(run, f"{side}-import", [sys.executable, "-c", verify], checkout, home)


def test_stage(args, run, revision):
    patch = args.patch.read_bytes()
    tests = args.tests.read_bytes()
    run.write("production.diff.patch", patch.decode("utf-8"))
    run.write("public-tests.py", tests.decode("utf-8"))
    run.save("input.json", dict(
        production_sha256=hashlib.sha256(patch).hexdigest(),
        tests_sha256=hashlib.sha256(tests).hexdigest(),
        expected_regressions=args.expected_regressions,
    ))
    compile(tests, str(args.tests), "exec")
    home = run.path / "test-home"
    home.mkdir()
    for side in ("clean", "candidate"):
        export(args.repo, revision, run.path / side)
    clean, candidate = run.path / "clean", run.path / "candidate"
    applied = execute(run, "apply", ["git", "apply", "-"], candidate, home, stdin=patch)
    if applied["exit_code"] != 0:
        return "patch_does_not_apply"

    built = execute(run, "compile", [sys.executable, "-m", "compileall", "-q", "markdown"], candidate, home)
    if built["exit_code"] != 0:
        return "implementation_gate_failed"

    relative_test = Path("tests/test_autose_acceptance.py")
    observed = {}
    for side, checkout in (("clean", clean), ("candidate", candidate)):
        if verify_import(run, side, checkout, home)["exit_code"] != 0:
            return "checkout_import_failed"
        with (checkout / relative_test).open("xb") as stream:
            stream.write(tests)
        result = execute(run, f"{side}-public", [
            sys.executable, "-m", "unittest", "-v", "tests.test_autose_acceptance",
        ], checkout, home)
        observed[side] = result

    suite_command = [sys.executable, "-m", "unittest", "discover", "tests", "-v"]
    suite = execute(run, "candidate-suite", suite_command, candidate, home)
    if suite["exit_code"] != 0:
        (clean / relative_test).unlink()
        execute(run, "clean-suite", suite_command, clean, home)
        return "candidate_suite_failed"
    before, after = observed["clean"], observed["candidate"]
    if before["counts"] is None or after["counts"] is None or suite["counts"] is None:
        return "missing_test_counts"
    if before["counts"]["tests"] != after["counts"]["tests"] or after["counts"]["tests"] == 0:
        return "public_test_discovery_mismatch"
    if after["exit_code"] != 0 or after["counts"]["passed"] != after["counts"]["tests"]:
        return "candidate_public_tests_failed_or_skipped"
    if before["exit_code"] != 1 or before["counts"]["failures"] + before["counts"]["errors"] != args.expected_regressions:
        return "clean_regression_expectation_not_met"
    return "passed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", type=int, choices=CASES, required=True)
    parser.add_argument("--repo", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="mode", required=True)
    commands.add_parser("files", help="List the pinned public source, tests, and project configuration.")
    source = commands.add_parser("source", help="Read a public file at the mapped application revision.")
    source.add_argument("path")
    check = commands.add_parser("check", help="Replay a local build and testing gate from supplied artifacts.")
    check.add_argument("--patch", type=Path, required=True)
    check.add_argument("--tests", type=Path, required=True)
    check.add_argument("--expected-regressions", type=int, required=True, choices=range(1, 11), metavar="1..10")
    check.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    base_branch, revision = CASES_BY_BASE[args.issue]
    args.repo = args.repo.resolve()
    if args.mode == "files":
        sys.stdout.buffer.write(git(args.repo, "ls-tree", "-r", "--name-only", revision, "--",
                                    *PUBLIC_DIRS, *PUBLIC_CONFIG))
        return 0
    if args.mode == "source":
        sys.stdout.buffer.write(application_file(args.repo, revision, args.path))
        return 0

    os.umask(0o077)
    run = Run(args.out.resolve(), "public-testing-replay")
    run.save("manifest.json", dict(issue=args.issue, revision=revision, base_branch=base_branch,
                                  mode="local_artifact_replay", model_calls=0, python=sys.version))
    try:
        outcome = test_stage(args, run, revision)
    except (OSError, SyntaxError, subprocess.SubprocessError, ValueError) as exc:
        run.save("runner-error.json", dict(type=type(exc).__name__, message=str(exc)))
        outcome = "runner_error"
    run.save("gate.json", dict(outcome=outcome))
    print(outcome)
    return 0 if outcome == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
