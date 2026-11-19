"""Post one verified independent review on the current fork PR head."""

import argparse
import os
from pathlib import Path

from .baseline import Run
from .github import API, GitHub
from .publish import read_json, verify_pr
from .review import parse_review
from .trigger import FORK


def post(review_dir, client, run):
    if read_json(review_dir / "gate.json")["outcome"] != "review_ready":
        raise ValueError("Review gate did not pass")
    if read_json(review_dir / "manifest.json")["mode"] != "live":
        raise ValueError("Only live review findings may be posted")
    record = read_json(review_dir / "pr.json")
    result = read_json(review_dir / "review-result.json")
    text = (review_dir / "review.md").read_text(encoding="utf-8")
    verdict = parse_review(text)
    if any(result.get(k) != v for k, v in verdict.items()):
        raise ValueError("Review findings and verdict metadata disagree")
    if (result["issue"], result["number"], result["head_sha"]) != (
        record["issue"], record["number"], record["head_sha"],
    ) or record["fork"] != FORK:
        raise ValueError("Review belongs to a different issue, PR or head")
    round_number = result["round"]
    if type(round_number) is not int or round_number not in (1, 2):
        raise ValueError("Review rounds are limited to two")

    number = int(record["number"])
    endpoint = f"{API}/pulls/{number}"
    verify_pr(client.request(endpoint), record)
    reviewer = client.request("/user")["login"]
    marker = f"<!-- autose-review:{record['issue']}:round-{round_number} -->"
    submitted = []
    for page in range(1, 11):
        rows = client.request(f"{endpoint}/reviews?per_page=100&page={page}")
        submitted.extend(row for row in rows if row["user"]["login"] == reviewer
                         and row["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"))
        if len(rows) < 100:
            break
    else:
        raise ValueError("Could not verify earlier review rounds")
    matching = [row for row in submitted if (row.get("body") or "").endswith(marker)]
    if matching:
        if len(matching) != 1 or matching[0]["commit_id"] != record["head_sha"]:
            raise ValueError("This review round already belongs to another PR revision")
        posted = matching[0]
    else:
        if round_number == 2:
            first = f"<!-- autose-review:{record['issue']}:round-1 -->"
            prior = [row for row in submitted if (row.get("body") or "").endswith(first)]
            if len(prior) != 1 or prior[0]["state"] != "CHANGES_REQUESTED" or prior[0]["commit_id"] == record["head_sha"]:
                raise ValueError("Round 2 requires a changed head after a round 1 change request")
        verify_pr(client.request(endpoint), record)
        posted = client.request(endpoint + "/reviews", dict(
            commit_id=record["head_sha"], event=verdict["verdict"],
            body=f"{text.rstrip()}\n\n{marker}",
        ))
    if posted["commit_id"] != record["head_sha"]:
        raise ValueError("GitHub posted the review on an unexpected commit")
    run.save("posted-review.json", dict(result, url=posted["html_url"]))
    run.write("review.md", text)
    verify_pr(client.request(endpoint), record)
    if verdict["route"] is None:
        return "posted"
    if round_number == 2:
        return "review_limit_reached"
    run.save("return-to-stage.json", dict(
        issue=record["issue"], number=number, reviewed_head=record["head_sha"],
        target_stage=verdict["route"], review_url=posted["html_url"], next_review_round=2,
    ))
    return f"route_to_{verdict['route'].lower()}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    token = os.getenv("AUTOSE_REVIEW_POST_TOKEN")
    if not token:
        parser.error("AUTOSE_REVIEW_POST_TOKEN is required")
    os.umask(0o077)
    run = Run(args.out.resolve(), "post-review")
    run.secret = token
    run.save("manifest.json", dict(parent_run=str(args.review_run.resolve()), fork=FORK))
    try:
        outcome = post(args.review_run, GitHub(token), run)
    except (OSError, KeyError, RuntimeError, ValueError, TypeError) as exc:
        run.save("error.json", dict(type=type(exc).__name__, message=str(exc)))
        outcome = "posting_failed"
    run.save("gate.json", dict(outcome=outcome))
    print(outcome)
    return 1 if outcome == "posting_failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
