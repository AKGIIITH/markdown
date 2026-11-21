"""Coordinate Requirements, Design, and Builder, with offline replay support."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from .baseline import CASES, GROQ_MODELS, Run, git
from .pilot import RELEASE_NOTES, ROOT


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


def coordinate(args, run, previous):
    shared = ["--issue", str(args.issue), "--out", str(run.path)]
    if args.issue_file:
        shared.extend(["--issue-file", str(args.issue_file.resolve())])
    if args.live:
        mode = ["--live", "--budget-confirmation", args.budget_confirmation]
        requirements = [
            "--skill", str(args.skill.resolve()), "--proposal-cap", str(args.requirements_cap),
            "--proposal-format", args.requirements_format, *mode,
        ]
        design_mode = builder_mode = mode
    else:
        fixtures = args.fixtures.resolve()
        requirements = [
            "--proposal", str(fixtures / "proposal.json"), "--parent-run", str(fixtures),
            "--fixture", str(fixtures / "quality.json"),
        ]
        design_mode = ["--fixture", str(fixtures / "design.json")]
        builder_mode = ["--fixture", str(fixtures / "builder.json")]

    def requirements_step(_prior):
        first = previous.get("requirements") or stage(
            run, "requirements", ["workflow.requirements", *shared, *requirements],
        )
        yield first
        if args.live and first["gate"] in {"route_to_requirements", "pause_for_material_ambiguity"} and first["artifact"]:
            feedback = Path(first["artifact"]) / "judgment.json"
            if feedback.is_file():
                run.event("repair_dispatch", from_stage="requirements_quality", to_stage="requirements", attempt=1)
                yield stage(run, "requirements", [
                    "workflow.requirements", *shared, *requirements, "--feedback", str(feedback),
                ])

    def design_step(prior):
        yield previous.get("design") or stage(run, "design", [
            "workflow.design", *shared, "--requirements-run", prior["artifact"],
            "--max-calls", str(args.design_calls), "--completion-cap", str(args.design_cap),
            "--final-completion-cap", str(args.design_final_cap), *design_mode,
        ])

    def build(prior, extra=(), *, reuse=False):
        sdk = ["--sdk-calls", str(args.builder_sdk_calls)] if args.builder_sdk_calls else []
        return (previous.get("builder") if reuse else None) or stage(run, "builder", [
            "workflow.builder", *shared, "--design-run", prior["artifact"],
            "--implementation-cap", str(args.implementation_cap), "--testing-cap", str(args.testing_cap),
            "--testing-context", args.testing_context, *sdk, *builder_mode, *extra,
        ])

    def builder_step(prior):
        yield build(prior, reuse=True)

    def test(prior):
        options = []
        if args.check_image:
            options = ["--check-image", args.check_image, "--release-note", RELEASE_NOTES[args.issue]]
        return stage(run, "testing", [
            "workflow.pilot", "--issue", str(args.issue), "check",
            "--out", str(run.path), "--builder-run", prior["artifact"], *options,
        ])

    steps = [("requirements", requirements_step, "passed"), ("design", design_step, "passed"),
             ("builder", builder_step, "ready_for_test_runner")]
    if not args.live or args.check_image:
        steps.append(("testing", lambda prior: [test(prior)], "passed"))

    def route(records):
        latest = {}
        for record in records:
            latest[record["stage"]] = record
            yield record
        first = latest.get("testing", {})
        if not (args.live and args.check_image and first.get("exit_code") != 0 and first.get("artifact")):
            return
        feedback = Path(first["artifact"])
        route_file = feedback / "return-to-stage.json"
        if not route_file.is_file():
            return
        target = read_json(route_file)["target_stage"]
        builder = latest["builder"]["artifact"]
        if target == "Testing":
            extra = ["--implementation-from", builder, "--testing-feedback", str(feedback)]
        elif target == "Implementation":
            extra = ["--repair-from", str(feedback)]
        else:
            return
        run.event("repair_dispatch", from_stage="testing", to_stage=target.lower(), attempt=1)
        repair = build(latest["design"], extra)
        yield repair
        if repair["exit_code"] == 0 and repair["gate"] == "ready_for_test_runner":
            yield test(repair)

    if args.builder_sdk_calls:
        from .sdk_builder import run_stage_graph

        yield from route(run_stage_graph(steps))
        return
    def run_steps():
        prior = None
        for _name, step, expected_gate in steps:
            for prior in step(prior):
                yield prior
            if prior["exit_code"] != 0 or prior["gate"] != expected_gate:
                break

    yield from route(run_steps())


def resumed_stages(parent, issue, revision, issue_digest, mode):
    manifest = read_json(parent / "manifest.json")
    if (
        manifest["issue"], manifest["revision"], manifest.get("issue_sha256"), manifest["mode"]
    ) != (issue, revision, issue_digest, mode):
        raise ValueError("Parent run has a different issue, revision, issue snapshot or mode")
    latest = {record["stage"]: record for record in read_json(parent / "stages.json")}
    reusable = {}
    for name, outcome in (("requirements", "passed"), ("design", "passed"), ("builder", "ready_for_test_runner")):
        row = latest.get(name)
        if not row or row["exit_code"] != 0 or row["gate"] != outcome or not row["artifact"]:
            break
        # GitHub artifacts retain paths from the previous runner. Resolve only
        # the recorded stage directory inside this controller's evidence.
        recorded = Path(row["artifact"])
        if recorded.parent.name != parent.name or recorded.name in ("", ".", ".."):
            raise ValueError(f"Invalid {name} handoff path in parent run")
        path = (parent / recorded.name).resolve()
        if path.parent != parent.resolve() or read_json(path / "gate.json")["outcome"] != outcome:
            raise ValueError(f"Invalid or nonlocal {name} handoff in parent run")
        receipt = read_json(path / "manifest.json")
        if (receipt.get("issue"), receipt.get("revision")) != (issue, revision):
            raise ValueError(f"Wrong issue or application revision in {name} receipt")
        if name == "builder" and not (path / "public-tests.py").is_file():
            break
        reusable[name] = {**row, "artifact": str(path), "reused": True}
    return reusable


def copy_reused_handoffs(run, previous):
    handoffs = {
        "requirements": ("accepted-requirements.json", "judgment.json"),
        "design": ("design.md", "design-evidence.json", "requirements.json"),
        "builder": ("diff.patch", "public-tests.py", "implementation-gate.json", "implementation-completion.txt"),
    }
    for name, row in previous.items():
        origin = Path(row["artifact"])
        destination = run.path / origin.name
        destination.mkdir()
        for file in ("manifest.json", "gate.json", *handoffs[name]):
            shutil.copyfile(origin / file, destination / file)
        if name == "builder":
            manifest = read_json(destination / "manifest.json")
            manifest["parent_run"] = previous["design"]["artifact"]
            (destination / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        row["reused_from"] = str(origin)
        row["artifact"] = str(destination)


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
    parser.add_argument("--model", choices=GROQ_MODELS, default=GROQ_MODELS[1])
    parser.add_argument("--requirements-format", choices=("json_object", "json_schema"), default="json_schema")
    parser.add_argument("--testing-context", choices=("patch_only", "retained"), default="patch_only")
    parser.add_argument("--builder-sdk-calls", type=int, help="Enable the LangGraph Builder with an explicit task call limit.")
    parser.add_argument("--check-image", help="Run Testing in this local Docker image before handing off to Release.")
    parser.add_argument("--issue-file", type=Path)
    parser.add_argument("--resume-from", type=Path, help="Reuse passed handoffs from one previous controller run.")
    parser.add_argument("--budget-confirmation")
    args = parser.parse_args()
    if args.live and not (args.skill and (args.budget_confirmation or "").strip() and os.getenv("GROQ_API_KEY")):
        parser.error("Live runs require --skill, --budget-confirmation and GROQ_API_KEY")
    if args.design_calls < 3 or min(args.requirements_cap, args.design_cap, args.design_final_cap,
                                    args.implementation_cap, args.testing_cap) < 1:
        parser.error("Design needs at least three calls and all completion caps must be positive")
    if args.builder_sdk_calls is not None and args.builder_sdk_calls < 1:
        parser.error("The Builder SDK call limit must be positive")

    os.umask(0o077)
    revision, _, issue_name = CASES[args.issue]
    issue_path = args.issue_file or ROOT / "experiment/issues" / issue_name
    try:
        issue_digest = hashlib.sha256(issue_path.read_bytes()).hexdigest()
        mode = "live" if args.live else "fixture"
        previous = resumed_stages(args.resume_from.resolve(), args.issue, revision, issue_digest, mode) if args.resume_from else {}
        if "builder" in previous:
            parent = read_json(args.resume_from / "manifest.json")
            if parent.get("builder_sdk_calls") != args.builder_sdk_calls:
                previous.pop("builder")
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    run = Run(args.out.resolve(), "controller")
    copy_reused_handoffs(run, previous)
    if args.live:
        os.environ["AUTOSE_GROQ_MODEL"] = args.model
        os.environ["AUTOSE_RATE_STATE"] = str(run.path / "provider-rate-state.json")
    run.save("manifest.json", dict(
        issue=args.issue, revision=revision, mode=mode, issue_sha256=issue_digest,
        parent_run=str(args.resume_from.resolve()) if args.resume_from else None,
        harness_commit=git(ROOT, "rev-parse", "HEAD").decode().strip(),
        requirements_format=args.requirements_format, testing_context=args.testing_context,
        builder_sdk_calls=args.builder_sdk_calls, model=args.model if args.live else None,
    ))
    records = []
    for record in coordinate(args, run, previous):
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
