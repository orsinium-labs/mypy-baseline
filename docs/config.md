# Configuration

The tool has a number of CLI flags to configure the behavior of `filter`. The default value for each flag can be specified in `pyproject.toml`. There are all the configuration options and their defaults:

```python
[tool.mypy-baseline]
# --baseline-path: the file where the baseline should be stored
baseline_path = "mypy-baseline.txt"
# --depth: cut path names longer than that many directories deep
depth = 40
# --allow-unsynced: do not fail for unsynced resolved errors
allow_unsynced = False
# --preserve-position: do not remove error position from the baseline
preserve_position = False
# --hide-stats: do not show stats and messages at the end
hide_stats = False
# --no-colors: do not use colors in stats
no_colors = False
# --ignore: regexes for error messages to ignore
ignore = []
```
