# Leading the way

This page provides guides and tips for the person who takes the initiative to integrate mypy-baseline with a project. If you are the person who works with a project already integrated with mypy-baseline and need survival tips, check out [Following the lead](./follower.md).

## Integrate mypy-baseline with the project

1. The [Usage](./usage.md) page covers the basic integration. To summarize, you generate the initial baseline with `mypy | mypy-baseline sync`, and then all consequentice runs of `mypy | mypy-baseline filter` will ignore these errors.
If you have something like [Taskfile](https://taskfile.dev/) or [Makefile](https://www.gnu.org/software/make/manual/make.html), it's good to provide tasks for both commands, for your team's convenience.
1. Start with the most friendly and relaxed mypy config. Allow everything that can be allowed. For instance, set `allow_redefinition = true`. That will allow you to focus on the most important errors for now.
1. `mypy-baseline.txt` should be committed into the repository, so it's always the same and up-to-date for everyone in the team.
1. Don't forget to integrate mypy-baseline with CI.
1. And lastly, tell your team about mypy, mypy-baseline, and how to use it. Write some internal documentation, make a tech talk, and support them when they struggle to understand why mypy complaints about something. It's a good idea to make a Slack channel where people can ask their mypy-related questions.

## Encourage your team to resolve old errors

The purpose of mypy-baseline not to let you ignore all existing errors in the project, but to let you resolve them gradually, start using mypy right now, and make sure nobody introduces new errors. That's why it's important to bring one day the number of mypy errors to zero. And that should be a team effort.

1. Foster the engineering culture of making things better. Tell them about [the boy scout rule](https://www.oreilly.com/library/view/97-things-every/9780596809515/ch08.html).
1. The colorful statistics mypy-baseline shows at the end of each run are designed to encourage people making these numbers smaller. You can help by posting this stats bi-weekly in Slack, so everyone sees the progress you all make.
1. On review, praise the people who reduced the number of lines in "mypy-baseline.txt".

## Review merge requests

1. Praise merge request author for removing lines from `mypy-baseline.txt`.
1. Question them for adding new lines in `mypy-baseline.txt`. There should be no new violations. Don't accumulate tech debt without a very good reason. Resolve all type errors right away whenever possible.
1. Question them adding `# type: ignore`. There (almost) always a way to resolve an error instead of just ignoring it. However, it's not always obvious how. Help them find the way.
1. If you see some mistakes in type annotations, gently tell them how to fix it.

## Resolve all type errors in the code

Your ultimate goal is to resolve all errors you have and get rid of mypy-baseline.

1. As mentioned in "Integrate mypy-baseline with the project", start with the most friendly and relaxed mypy config.
1. Try adding some third-party plugins, like [django-stubs](https://github.com/typeddjango/django-stubs). Sometimes, they bring the number of detected violations down, not up. If that the case for your project, use it. If not, don't use them just yet, leave it for later.
1. When you resolve at least 80% of existing errors, make mypy config a bit more strict, and repeat the process. Then make it more strict again.
1. When you're happy with the config, it's time to integrate mypy-plugins and stubs you haven't integrated yet. See [awesome-python-typing](https://github.com/typeddjango/awesome-python-typing) for what is available.

## Deal with false-positives

It's possible (especially if you use third-party mypy plugins) that one day you'll encounter a false-positive that produces tons of violations for your project. If you sync these violations with the baseline or add `# type: ignore` for each, you still will get them when a new code is added. And that will confuse people and encourage a bad practice of mindlessly ignoring new violations. Don't do that. Instead, use `ignore` [configuration option](./config.md) to ignore the troublesome error altogether until it gets fixed upstream.
