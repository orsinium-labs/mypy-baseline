# mypy-baseline

A CLI tool for painless integration of mypy with an existing Python project. When you run it for the first time, it will remember all type errors that you already have in the project (generate "baseline"). All consequentive runs will ignore these errors and report only ones that you introduced after that.

Additionally, the tool will show you what progress you made since the last baseline, to encourage your team to resolve mypy errors:

![example of the command output](./example.png)

Features:

+ Battle-tested.
+ Fast and simple.
+ Pure Python.
+ No mypy patching or dirty magic. The tool works exclusively with the stdout of mypy.
+ Nice stats with colors.
+ Can detect exactly what errors were introduced and what errors were resolved, even if they are in the same file.
+ Baseline is carefully crafted to avoid merge conflicts.
+ Baseline is human-readable, and diffs are informative. The reviewers of your PR will know exactly what errors you resolve and what errors you introduced.

## Installation

```bash
python3 -m pip install mypy-baseline
```

## Usage

First of all, you need to create the baseline (will be stored in `mypy-baseline.txt` by default):

```bash
mypy --show-codes | mypy-baseline sync
```

After that, you can pipe mypy output into `mypy-baseline filter`, and it will filter out all issues that are already in the baseline:

```bash
mypy --show-codes | mypy-baseline filter
```

If you introduce new errors, resolve them. If you resolve existing errors, run `mypy-baseline sync` again to re-generate baseline. In both cases, mypy-baseline will tell you what's wrong and what to do. Enjoy the ride!

## Configuration

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
```
