# It's hard to tell what went wrong when I mistype a filename

I use `python -m markdown` to convert my lecture notes. Yesterday I typed
`lecture-notse.md` by mistake. The command printed a long Python traceback,
and I had to read to the bottom to work out what I should fix.

Could the command make this easier to understand? I also run it from a
script sometimes, so the script still needs to know when conversion failed.
