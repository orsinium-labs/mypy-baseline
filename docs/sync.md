# sync

The `mypy-baseline sync` command is the first one you run. It creates a new baseline file or synchronizes the changes with an existing one.

```bash
mypy | mypy-baseline sync
```

The baseline file (`mypy-baseline.txt` by default) contains all errors that mypy spits out with line numbers replaced with zeros and colors removed. All errors recorded in the baseline will be filtered out from the future mypy runs by `mypy-baseline filter`.

The lines in the baseline come in the same order as mypy produeces them. This order is fragile, and the order of files analyzed (and so the lines in the baseline) might change as the dependency graph between modules changes and even be different on different machines. When syncing the changes with an existing baseline, we try to preserve the lines order there, but sometimes it cannot be done, and the lines may jump around. If that causes merge conflicts, simply re-run `sync` instead of trying to fix conflicts manually.

## Jupyter notebooks

All mypy-baseline commands support [nbQA](https://github.com/nbQA-dev/nbQA) for checking [Jupyter notebooks](https://jupyter.org/):

```bash
python3 -m pip install nbqa
nbqa mypy . | mypy-baseline sync
```
