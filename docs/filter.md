# filter

The `mypy-baseline filter` command is the one you'll be running the most. It consumes mypy output from stdin and spits it into stdout with old violations (the ones recorded in the baseline file) removed.

```bash
mypy | mypy-baseline filter
```

If the command says that you have fixed every single violation, a possible cause of it might be that mypy has exploded and reported no type violations. Check its output, it should have a traceback. If not, run mypy again with `--show-traceback` specified.
