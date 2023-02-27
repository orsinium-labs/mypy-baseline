# suggest

The `mypy-baseline suggest` command checks if your current branch fixes enough errors from the baseline (1 by default, can be changed with the `-n` flag), and if not suggest you a semi-random error from the baseline to fix.

```bash
mypy-baseline suggest
```

## CI

The command is designed to be integrated with CI, and will do its best to correctly detect the target branch and produce stable results for the same PR.

Also, there is a native integration with GitLab CI that adds suggestions as comments to MRs. To use it:

1. Set `GITLAB_CI` environment variable with an [access token](https://gitlab.com/-/profile/personal_access_tokens) of the user that should be used to add the comment.
1. Install [requests](https://requests.readthedocs.io/en/latest/): `python3 -m pip install requests`
1. Run `mypy-baseline suggest` with `--comment` flag.

For example:

```yaml
mypy-baseline suggest:
  # ...
  rules:
    - if: "$CI_MERGE_REQUEST_ID"
  before_script:
    - python -m pip install mypy-baseline requests
  script:
    - git fetch origin master
    - >
      mypy-baseline suggest
      --exit-zero
      --default-branch=origin/master
      --comment
```

With other CI providers, you can try piping the command output into [reviewdog](https://github.com/reviewdog/reviewdog).
