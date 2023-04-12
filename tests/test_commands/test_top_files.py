from __future__ import annotations

from pathlib import Path

from .helpers import LINE1, LINE2, NOTEBOOK_LINE1, run


def test_top_files(tmp_path: Path):
    blpath = tmp_path / 'bline.txt'
    blpath.write_text(f'{LINE1}{LINE2}')
    cmd = ['top-files', '--baseline-path', str(blpath), '--no-color']
    actual = run(cmd)
    assert 'views.py' in actual
    assert 'settings.py' in actual


def test_top_notebook(tmp_path: Path):
    blpath = tmp_path / 'bline.txt'
    blpath.write_text(f'{NOTEBOOK_LINE1}')
    cmd = ['top-files', '--baseline-path', str(blpath), '--no-color']
    actual = run(cmd)
    assert 'fail.ipynb' in actual
