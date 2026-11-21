# Issue 2 public test report

Status `passed` at application revision `1e2b7f27aeefe70057025a1da0d10006dd11ad48`.
Both checkouts use the same public test module.

| Check | Exit | Seconds | Passed | Skipped | Failures | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| [apply](apply.json) | 0 | 0.003 |  |  |  |  |
| [compile](compile.json) | 0 | 0.084 |  |  |  |  |
| [clean-public](clean-public.json) | 1 | 0.096 | 3 | 0 | 2 | 0 |
| [candidate-public](candidate-public.json) | 0 | 0.068 | 5 | 0 | 0 | 0 |
| [candidate-suite](candidate-suite.json) | 0 | 1.902 | 1117 | 111 | 0 | 0 |

Each command record has matching stdout and stderr logs.
