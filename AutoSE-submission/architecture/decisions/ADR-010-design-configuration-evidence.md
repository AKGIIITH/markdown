# ADR-010 — Include pinned configuration dependencies in Design

## Status

Experimental. Extends ADR-004 and ADR-005. An Issue #3 replay passed the
structural gate. The runtime check still exposed a wrong default.

## Context

The Issue #3 Planner successfully found and read the relevant table source
and public tests. The source range covered table creation and omitted both the
extension's configuration and the shared setter. The final draft proposed
`None` as a default for a string option. The pinned setter treats that default
as a request for boolean parsing. The draft also failed to cite the public
test it read.

## Decision

When lookup selects an extension module, include a bounded excerpt for its
extension subclass and the shared `Extension.setConfig` implementation. Read
both at the application pin. Record the additional excerpts as harness
retrieval and keep the shared dependency read-only for Builder. Ask the final
Design writer to cite the exact public test path and explain the example it
used. Keep the accepted criteria, lookup tools, model and caps fixed.

## Consequences

The final writer receives the configuration contract without an extra tool
call. The approach relies on the pinned Python-Markdown extension layout and
increases the text in the final request. It still depends on the model
choosing relevant source and public tests. The gate still requires citations
and a public test mapping for every accepted criterion.

The replay cited the public test successfully and finished below the cap.
It still proposed the wrong default despite the setter excerpt. The public
runner exposed the contradiction when it executed the Builder patch.
