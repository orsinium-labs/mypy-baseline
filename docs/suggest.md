# suggest

The `mypy-baseline suggest` command checks if your current branch fixes enough errors from the baseline (1 by default, can be changed with the `-n` flag), and if not suggest you a semi-random error from the baseline to fix.

```bash
mypy-baseline suggest
```

The command is designed to be integrated with CI, and will do its best to correctly detect the target branch and produce stable results for the same PR.

To improve user experience, you can pipe the output into [reviewdog](https://github.com/reviewdog/reviewdog) to get suggestions as review comments:

```bash
mypy-baseline suggest | reviewdog \
    -efm='%f:%l: %m' \
    -name=mypy-baseline \
    -reporter=gitlab-mr-discussion \
    -filter-mode=nofilter
```
