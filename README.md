# mypy-baseline

A CLI tool for painless integration of mypy with an existing Python project. When you run it for the first time, it will remember all type errors that you already have in the project (generate "baseline"). All consecutive runs will ignore these errors and report only ones that you introduced after that.

Additionally, the tool will show you what progress you made since the last baseline, to encourage your team to resolve mypy errors:

![example of the command output](./assets/example.png)

Features:

+ Battle-tested.
+ Fast and simple.
+ Pure Python.
+ No mypy patching or dirty magic. The tool works exclusively with the stdout of mypy.
+ Nice stats with colors.
+ Can detect exactly what errors were introduced and what errors were resolved, even if they are in the same file.
+ Baseline is carefully crafted to avoid merge conflicts.
+ Baseline is human-readable, and diffs are informative. The reviewers of your PR will know exactly what errors you resolve and what errors you introduced.
+ Track the progress you make with git-based history of changes and burndown chart of resolved type violations.
+ Ignore specific error messages (using regular expressions) and error categories, so that buggy mypy plugins don't bother you with false-positives.

## Installation

```bash
python3 -m pip install mypy-baseline
```

## Usage

Create the baseline (it will be stored in `mypy-baseline.txt` by default):

```bash
mypy | mypy-baseline sync
```

After that, you can pipe mypy output into `mypy-baseline filter`, and it will filter out all issues that are already in the baseline:

```bash
mypy | mypy-baseline filter
```

If you introduce new errors, resolve them. If you resolve existing errors, run `mypy-baseline sync` again to re-generate baseline. In both cases, mypy-baseline will tell you what's wrong and what to do. Enjoy the ride!

Read more in the documentation: [mypy-baseline.orsinium.dev](https://mypy-baseline.orsinium.dev/)
