# Issue #3 SDK trace

The local harness read [Issue #3](https://github.com/AKGIIITH/markdown/issues/3)
from the fork and saved its title and body as Markdown. The input snapshot
had SHA-256 `86fae8b7b71fc06c776552167e7d67ae6404a2aa0a615b4525c20ede8a1447ad`.
Application pin `2c96e36ba4750cf18583d62e2fcecff49e077419` and harness
revision `15484c0` were recorded independently.

## How the inputs travel

1. Requirements receives the issue Markdown in a JSON `issue` field of the
   model request. The Requirements skill is included in the system message.
   A second request judges the proposed criteria against the original issue.
2. Design receives the issue, accepted criteria, pin, and contents of
   `architecture/ARCHITECTURE.md` in its request. A lookup reply contains a
   named function, JSON arguments, and a call ID. For example, a Planner can
   request `read_file` with
   `{"path":"markdown/extensions/tables.py","start":1,"end":120}`.
3. The Python dispatcher validates the path and inclusive line range and
   reads the Git object at the pinned SHA. It returns numbered text and
   range metadata. The next request includes that result as a tool message
   associated with the original call ID. The Design writer receives the
   collected excerpts as text in a fresh request.
4. The Builder receives the accepted Design and raw excerpts. LangGraph
   routes its calls between the model and the tool dispatcher. A focused
   `ask_planner` question goes to a separate Planner request and comes back
   as a tool result in Builder's conversation. The artifact submission ends
   the task and gives the patch or test module to the trusted gate.

## Fresh run

| Step | Result |
| --- | --- |
| Requirements proposal | The strict JSON request received HTTP 400 `json_validate_failed`. The existing text fallback returned a complete proposal, and local validation passed. |
| Requirements quality | The model approved all five criteria as grounded and testable but flagged empty-string behavior, leading or trailing spaces, and repeated spaces as blocking questions. The controller recorded `pause_for_material_ambiguity`. |
| Design, Implementation, Testing, Release, Review | Skipped by the fresh run because the Requirements gate paused. |

Known usage was 5,662 tokens across the two successful responses. Usage for
the rejected request was unreported. The authoritative issue explicitly
asks for a single class, two classes, and the behavior when the option is
omitted. It does not specify those extra whitespace cases.

## Separate replay from accepted Design

The replay reused the earlier accepted Design for the byte-identical issue.
The original Design run found `markdown/extensions/tables.py` and
`tests/test_syntax/extensions/test_tables.py`, read lines 1–120 of each,
and added the pinned extension configuration snippets. Its final text
passed the structural gate. The subsequent local test run established
that the proposed `None` default would reject ordinary class strings.
Reusing this handoff tests whether Builder catches that documented failure
mode through its own investigation.

Groq rejected the first Builder request with HTTP 429
`rate_limit_exceeded`. The response reported a 200,000-token daily
allowance, 199,504 already used, and 4,758 requested. It returned
`Retry-After: 1842`. There was no model reply or reported usage for that
request. This replay did not produce a patch or public tests.

## Expected and observed stages

| Expected | Observed in the fresh run and replay |
| --- | --- |
| Issue and architecture reach Planner | The actual fork issue reached Requirements. The fresh run paused before the architecture was sent. The matching earlier Design request contains the architecture text and the exact same issue snapshot. |
| Planner locates files and writes a design | Skipped in the fresh run. The earlier accepted Design used live filename lookups and line reads. |
| Builder investigates, asks for help if needed, implements and tests | This replay reached the provider and was quota-limited before its first model reply. In the previous live SDK attempt a public source read succeeded. In the scripted SDK replay a clarification made the round trip and the candidate passed Testing with 3 public passes, 1,115 suite passes, and 111 skips. |
| A real PR is opened for the exact tested revision | Skipped. No live candidate had passed Testing. The scripted run reached local Release preflight only. |
| A fresh Reviewer checks that PR | Skipped. The hosted reviewer requires the PR and its exact-head CI evidence. |

The two current attempts reported 5,662 tokens across successful responses,
with two requests of unreported usage. Neither stop was caused by response
length. The previous test writer that ended with `finish_reason=length`
was a separate experiment.
