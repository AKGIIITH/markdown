# Adding linenums to a fenced code block stops the document from rendering

I use Python-Markdown to render code examples and handle highlighting in
the browser. A Python code block renders correctly until I add the
`linenums` attribute. After that, converting the document raises an exception.

## How to reproduce

Enable `fenced_code` and `attr_list`, leave `codehilite` disabled, and
convert this Markdown:

~~~~markdown
```{.python linenums}
print(1)
```
~~~~

## What I observed

- `.python` renders a Python code block containing `print(1)`.
- `.python linenums` raises `TypeError: cannot serialize None (type NoneType)`.
- `.python linenums=true` raises `TypeError: cannot serialize True (type bool)`.

## What I expected

The document should render in both cases. The code text and its Python
language class should be preserved, and the enabled `linenums` attribute
should be available to the browser on the `<code>` element.

Reproduced on commit `2c96e36ba4750cf18583d62e2fcecff49e077419`.
Original report: https://github.com/Python-Markdown/markdown/issues/1713
