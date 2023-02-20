# top-files

The `mypy-baseline top-files` command lists files with the most type violations.

```bash
mypy-baseline top-files
```

This is a good place to start if you're looking for something to fix. The top files are either the most problematic ones (and so need your attention the most) or there is some small error that produces a lot of error (and so fixing this small thing is a quick win).

You can get stats grouped for different levels of directories (for instance, for django apps) by setting a value for the `--depth` CLI flag.
