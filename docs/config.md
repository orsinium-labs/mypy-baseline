# Configuration

The tool has a number of CLI flags to configure the behavior of `filter`. The default value for each flag can be specified in `pyproject.toml`. There are all the configuration options and their defaults:

```toml
[tool.mypy-baseline]
# --baseline-path: the file where the baseline should be stored
baseline_path = "mypy-baseline.txt"
# --depth: cut path names longer than that many directories deep
depth = 40
# --allow-unsynced: do not fail for unsynced resolved errors
allow_unsynced = false
# --preserve-position: do not remove error position from the baseline
preserve_position = false
# --hide-stats: do not show stats and messages at the end
hide_stats = false
# --no-colors: do not use colors in stats
no_colors = false
# --ignore: regexes for error messages to ignore, e.g. ".*Enum.*"
ignore = []
# --ignore-categories: categories of mypy errors to ignore, e.g. "note" or "call-arg"
ignore_categories = []
```
