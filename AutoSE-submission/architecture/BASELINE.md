# Baseline AutoSE architecture

The application guide describes how Python-Markdown works. The AutoSE architecture describes how an issue moves through the agents. We needed both because a plan can name a real file and still misunderstand its configuration API. [Application guide](ARCHITECTURE.md) · [Component view](views/component.md)

## Why group six stages into four jobs?

The initial sketch treated the six stages as four responsibilities. Requirements and Design share a reading of the issue. The Planner first makes that reading testable, then looks at the code. Implementation and Testing share a candidate. The Builder can turn a failing test into a focused edit. Release owns a narrower task: publish precisely the tree that passed. Review needs a fresh start and only the public issue, diff and current source. The accepted baseline gave Release to a script. Planner, Builder and Reviewer are separate roles that can use the same model. [Original decision](decisions/ADR-001-agent-roles.md)

## What crossed each boundary?

The controller passed the accepted spec and public repository map to Design. The design named files and functions. The Builder received that plan with bounded public source, produced edits and wrote tests. A separate runner compared clean and candidate revisions, then ran the existing suite. Release received the tested patch digest, base and issue number. The Reviewer inspected the published commit after CI. The poster recorded its verdict and return stage. A human could close, request changes or merge. [Stage map](views/stages.md)

## What the experiments changed

The early jobs suffered from provider formatting errors, missing public-test reads and disagreement between a design and a real API. Strict structure, a separate quality judgement and focused source improved specific gates. LangGraph added bounded lookups and an explicit question back to the Planner. Saved handoffs made a repaired submission or test writer cheap to replay. The isolated test runner and pre-publication lint checks caught errors that compilation missed. A later small-patch review path uses deterministic source reads and a single independent verdict call. The role split stayed stable while these handoffs and failure paths changed. [Final observed sequence](views/final-demo.md)
