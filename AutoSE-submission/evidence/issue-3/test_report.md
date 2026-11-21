# Issue 3 public test report

Status `passed` at application revision `2c96e36ba4750cf18583d62e2fcecff49e077419`.
Both checkouts use the same public test module.

| Check | Exit | Seconds | Passed | Skipped | Failures | Errors |
| --- | --- | --- | --- | --- | --- | --- |
| [apply](apply.json) | 0 | 0.003 |  |  |  |  |
| [compile](compile.json) | 0 | 0.086 |  |  |  |  |
| [clean-public](clean-public.json) | 1 | 0.116 | 1 | 0 | 0 | 3 |
| [candidate-public](candidate-public.json) | 0 | 0.088 | 4 | 0 | 0 | 0 |
| [candidate-suite](candidate-suite.json) | 0 | 1.956 | 1116 | 111 | 0 | 0 |

Each command record has matching stdout and stderr logs.
