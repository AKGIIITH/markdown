"""Validate a GitHub issue trigger before model or write credentials are used."""

import argparse
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from .baseline import CASES


FORK = "AKGIIITH/markdown"
TRIGGER_LABEL = "autose:run"
TRIGGER_COMMENT = "/autose run"
REVIEW_COMMENT = "/autose review"


def selected_issue(event, kind, actor):
    repo = event.get("repository", {}).get("full_name")
    issue = event.get("issue", {})
    number = issue.get("number")
    sender = event.get("sender", {}).get("login")
    if (repo != FORK or not isinstance(actor, str) or not actor
            or not isinstance(sender, str) or sender.casefold() != actor.casefold()
            or type(number) is not int or number not in CASES
            or issue.get("state") != "open" or "pull_request" in issue):
        return None
    if kind == "issues" and event.get("action") == "labeled":
        return issue if event.get("label", {}).get("name") == TRIGGER_LABEL else None
    if kind == "issue_comment" and event.get("action") == "created":
        comment = event.get("comment", {})
        author = comment.get("user", {}).get("login")
        return issue if author == sender and comment.get("body", "").strip() == TRIGGER_COMMENT else None
    return None


def selected_review(event, kind, actor):
    issue = event.get("issue", {})
    comment = event.get("comment", {})
    sender = event.get("sender", {}).get("login")
    number = issue.get("number")
    if (kind == "issue_comment" and event.get("action") == "created"
            and event.get("repository", {}).get("full_name") == FORK and actor
            and sender == actor and comment.get("user", {}).get("login") == sender
            and comment.get("body", "").strip() == REVIEW_COMMENT and "pull_request" in issue
            and issue.get("state") == "open" and type(number) is int and number > 0):
        return number
    return None


def may_trigger(token, actor):
    endpoint = f"https://api.github.com/repos/{FORK}/collaborators/{quote(actor, safe='')}/permission"
    request = Request(endpoint, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "User-Agent": "autose-a3-baseline/1",
    })
    with urlopen(request, timeout=20) as response:
        role = json.load(response)
    return role.get("role_name") in ("admin", "maintain") or role.get("permission") == "admin"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-file", type=Path, required=True)
    parser.add_argument("--event-name", required=True)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--issue-out", type=Path)
    parser.add_argument("--outputs", type=Path, help="Append the authorized issue or review PR to GitHub outputs.")
    args = parser.parse_args()
    event = json.loads(args.event_file.read_text(encoding="utf-8"))
    issue = selected_issue(event, args.event_name, args.actor)
    review = selected_review(event, args.event_name, args.actor)
    if issue is None and review is None:
        return 0
    if args.issue_out:
        if issue is None:
            return 0
        title = issue.get("title") or ""
        body = issue.get("body") or ""
        args.issue_out.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
        return 0
    if not may_trigger(os.environ["GITHUB_TOKEN"], args.actor):
        return 0
    if args.outputs:
        with args.outputs.open("a", encoding="utf-8") as stream:
            if issue:
                print(f"issue={issue['number']}", file=stream)
            else:
                print(f"review_pr={review}", file=stream)
    elif issue:
        print(issue["number"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
