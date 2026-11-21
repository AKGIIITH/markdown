# Private acceptance tests

The evaluator keeps the 15 acceptance tests outside the Git checkout, three
for each of the five public issues. In the assignment workspace they are in
the sibling directory `../hidden_tests/` relative to the repository root.
This directory records the evaluation protocol. The model jobs receive public
issue text, the pinned application source, and public tests.

The evaluator runs the tests against the mapped clean revision and the frozen
candidate commit after the public testing gate. The evaluator records counts
in the [results ledger](../../results/runs.md).
