# Following the lead

This page is a collection survival tips for people who work on a project already integrated with mypy-baseline. If you're instead the person making the first steps of integrating mypy-baseline with the project, check out [Leading the way](./leader.md) first.

And whatever happens, be brave. Tinker, experiment, hack, and observe.

## Resolve new errors

When mypy-baseline tells you that you introduced new errors and you need to resolve them, have a look at the very top of the command output, above "total errors". There you see the original output of mypy with filtered out old violations. Each error shown there is something you introduced since the last sync. That's what you need to resolve.

1. Start from going to the named file and line number to see what's the code that caused it.
1. Read the error message. It says exactly what's wrong.
1. If you don't understand the error, google it. Chances are you're not the first one to struggle with it.
1. Use [reveal_type](https://adamj.eu/tech/2021/05/14/python-type-hints-how-to-debug-types-with-reveal-type/) to show the type of a variable. Your IDE may show different types (because it's likely not using mypy for that), so always double-check what exactly mypy sees.
1. If you still can't figure it out, don't hesitate to ask your co-workers. You all can learn something from it.
1. The last resort is to add `# type: ignore[error-code]` to the line that caused the issue. Don't overuse it, though, each error reported by mypy is reported for a reason.

## Resolve old errors

1. Run bare-bones mypy without using mypy-baseline, and that will spit out all existing type errors.
1. Run `mypy-baseline top-files`. These are the files that need the most attention. Either they have lots of problems, or there is a small error (like a wrong annotation for a base class method) that causes a cascade of type violations and so fixing it would be a quick win.
1. Don't forget to run `mypy | mypy-baseline sync` when you finish.

## Resolve suggested errors

If your team uses [mypy-baseline suggest](./suggest.md) on CI, you may get in your MRs suggestions from mypy-baseline on what errors to resolve.

1. Copy the suggested error.
1. Open the baseline file mentioned in the comment (`mypy-baseline.txt` by default).
1. Find and remove the suggested error from the file and save the changes.
1. Run `mypy | mypy-baseline filter` and it should show you that error with the correct line number.
1. Go to the reported line of code and solve the issue.

## Keep mypy-baseline in sync

1. By default, mypy-baseline will fail if there are resolved but unsynced errors. The reason for that is to keep `mypy-baseline.txt` always up-to-date. If you don't do that, it will be hard for others to see what errors their changes resolved. Think about others.
1. If mypy-baseline tells you "your changes resolved existing violations", you need to run `mypy | mypy-baseline sync`. It will actualize `mypy-baseline.txt` for you.

## Deal with merge conflicts

The order of lines in the baseline file depends on the order in which mypy resolved the files. And that order may be different on different machines. We try to minimize such cases and avoid lines jumping around, but it's still possible. And when it happens, it may cause merge conflicts.

The best you can do when you encounter a merge conflict is to re-generate the baseline by running `mypy | mypy-baseline sync`.

## Deal with false-positives

Mypy and its ecosystem is widely used, battle-tested, and made by smart people. False-positives are possible but rare. When you see a violation reported by mypy, considering it a false-positive and simply ignoring must be your very last option.

1. Check if all you type annotations are correct. For instance, if you assign to a variable a `list`, then assign to the same variable a `tuple`, and mypy complaints about it, consider annotating the variable as a `Sequence` or similar.
1. Some errors might be a sign of a bad design. For instance, mypy requires you to follow [Liskov substitution principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle), and methods violating it will be reported. The best you can do in such cases is to refactor it.
1. Don't be afraid to ask for help your coworkers or online. Some errors might look cryptic for newcomers, and nobody will blame you for not understanding how to fix it right away.
