# history

The `mypy-baseline history` command prints in terminal commits that modified the baseline file and how many lines it had.

The command works with [git log](https://git-scm.com/docs/git-log). So, to run the command, you need the baseline to be tracked in a git repository and git to be installed on the machine.

```bash
mypy-baseline history
```

Columns:

1. `date` and `time` is when the commit was created (`%cI`).
1. `res` is how many lines there were in the baseline after the commit.
1. `old` is how many lines there were in the baseline before the commit.
1. `fix` is how many lines were removed from the baseline.
1. `new` is how many lines were added into the baseline
1. `commit` is the SHA256 has of the commit (`%H`).
1. `author` is the email of the commit author (`%ae`).

![example of the command output](./assets/history.png)
