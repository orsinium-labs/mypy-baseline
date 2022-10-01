from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from .._git import get_commits
from ._base import Command


class Plot(Command):
    """Draw the graph of how the baseline changed over time.

    Requires plotnine to be installed.
    """
    @classmethod
    def init_parser(cls, parser: ArgumentParser) -> None:
        super().init_parser(parser)
        parser.add_argument(
            '--output', type=Path, default=Path('mypy-baseline.png'),
            help='the path to save the file to',
        )

    def run(self) -> int:
        import pandas
        import plotnine as gg
        commits = list(get_commits(self.config.baseline_path))

        prev_count: int | None = None
        for commit in commits:
            commit.fix_lines_count(prev_count)
            prev_count = commit.lines_count

        commits = commits[1:]  # drop the oldest commit
        df = pandas.DataFrame(c.as_dict() for c in commits)
        df['created_at'] = pandas.to_datetime(df.created_at, utc=True)
        graph = (
            gg.ggplot(df, gg.aes(x='created_at', y='lines_count'))
            + gg.geom_line()
            + gg.geom_point(gg.aes(color='deletions > insertions'))
            + gg.ylim(0, max(c.lines_count for c in commits) + 5)
            + gg.theme(axis_text_x=gg.element_text(rotation=45, hjust=1))
            + gg.xlab('commit time')
            + gg.ylab('unresolved issues')
        )
        graph.save(self.args.output)
        return 0
