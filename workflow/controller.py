"""Coordinate Requirements, Design, and Builder, with offline replay support."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from .baseline import CASES, Run, git
from .pilot import ROOT


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def stage(run, name, argv):
    command = [sys.executable, "-m", *argv]
    run.event("stage_start", stage=name)
    start = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    run.write(f"{name}.stdout.log", result.stdout)
    run.write(f"{name}.stderr.log", result.stderr)
    record = dict(stage=name, command=command, exit_code=result.returncode,
                  seconds=round(time.monotonic() - start, 3), gate="runner_failed", artifact=None)
    # Requirements can print both its proposal and its subsequent quality run.
    # Use the last run directory under the controller's artifact root.
    for line in reversed(result.stdout.splitlines()):
        if not line.startswith("/"):
            continue
        path = Path(line).resolve()
        if path.is_relative_to(run.path.resolve()) and (path / "gate.json").is_file():
            record["gate"] = read_json(path / "gate.json")["outcome"]
            record["artifact"] = str(path)
            break
    run.event("stage_end", stage=name, gate=record["gate"], exit_code=result.returncode)
    return record


def coordinate(args, run):
    shared = ["--issue", str(args.issue), "--out", str(run.path)]
    if args.issue_file:
        shared.extend(["--issue-file", str(args.issue_file.resolve())])
    if args.live:
        mode = ["--live", "--budget-confirmation", args.budget_confirmation]
        requirements = ["--skill", str(args.skill.resolve()), "--proposal-cap", str(args.requirements_cap), *mode]
        design_mode = builder_mode = mode
    else:
        fixtures = args.fixtures.resolve()
        requirements = [
            "--proposal", str(fixtures / "proposal.json"), "--parent-run", str(fixtures),
            "--fixture", str(fixtures / "quality.json"),
        ]
        design_mode = ["--fixture", str(fixtures / "design.json")]
        builder_mode = ["--fixture", str(fixtures / "builder.json")]

    first = stage(run, "requirements", ["workflow.requirements", *shared, *requirements])
    yield first
    if first["exit_code"] != 0 or first["gate"] != "passed":
        return

    design = stage(run, "design", [
        "workflow.design", *shared, "--requirements-run", first["artifact"],
        "--max-calls", str(args.design_calls), "--completion-cap", str(args.design_cap),
        "--final-completion-cap", str(args.design_final_cap), *design_mode,
    ])
    yield design
    if design["exit_code"] != 0 or design["gate"] != "passed":
        return

    builder = stage(run, "builder", [
        "workflow.builder", *shared, "--design-run", design["artifact"],
        "--implementation-cap", str(args.implementation_cap), "--testing-cap", str(args.testing_cap),
        *builder_mode,
    ])
    yield builder
    if builder["exit_code"] != 0 or builder["gate"] != "ready_for_test_runner" or args.live:
        return

    yield stage(run, "testing", [
        "workflow.pilot", "--issue", str(args.issue), "check",
        "--out", str(run.path), "--builder-run", builder["artifact"],
    ])


def summarize_usage(run):
    tokens = {}
    unknown = []
    for path in sorted(run.path.glob("*/attempt-*-usage.json")):
        row = read_json(path)
        total = (row.get("usage") or {}).get("total_tokens")
        if row.get("id") and type(total) is int:
            tokens[row["id"]] = total
        else:
            unknown.append(str(path.relative_to(run.path)))
    run.save("usage-summary.json", dict(known_total_tokens=sum(tokens.values()), response_tokens=tokens,
                                       unknown_attempts=unknown))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--issue", type=int, choices=CASES, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--design-calls", type=int, required=True)
    parser.add_argument("--design-cap", type=int, required=True)
    parser.add_argument("--design-final-cap", type=int, required=True)
    parser.add_argument("--implementation-cap", type=int, required=True)
    parser.add_argument("--testing-cap", type=int, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixtures", type=Path)
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--skill", type=Path)
    parser.add_argument("--requirements-cap", type=int, default=1800)
    parser.add_argument("--issue-file", type=Path)
    parser.add_argument("--budget-confirmation")
    args = parser.parse_args()
    if args.live and not (args.skill and (args.budget_confirmation or "").strip() and os.getenv("GROQ_API_KEY")):
        parser.error("Live runs require --skill, --budget-confirmation and GROQ_API_KEY")
    if args.design_calls < 3 or min(args.requirements_cap, args.design_cap, args.design_final_cap,
                                    args.implementation_cap, args.testing_cap) < 1:
        parser.error("Design needs at least three calls and all completion caps must be positive")

    os.umask(0o077)
    run = Run(args.out.resolve(), "controller")
    run.save("manifest.json", dict(
        issue=args.issue, revision=CASES[args.issue][0], mode="live" if args.live else "fixture",
        harness_commit=git(ROOT, "rev-parse", "HEAD").decode().strip(),
    ))
    records = []
    for record in coordinate(args, run):
        records.append(record)
        run.save("stages.json", records)
    summarize_usage(run)
    last = records[-1]
    outcome = last["gate"]
    run.save("gate.json", dict(outcome=outcome, last_stage=last["stage"], artifact=last["artifact"]))
    print(outcome)
    return 0 if last["exit_code"] == 0 and outcome in ("passed", "ready_for_test_runner") else 1


if __name__ == "__main__":
    raise SystemExit(main())
