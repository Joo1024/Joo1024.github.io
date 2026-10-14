"""Shared setup for isolated content fixtures using the real site templates."""
from pathlib import Path
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://example.com/sanctum/'


def create_content(root):
    content = root / 'content'
    content.mkdir()
    shutil.copyfile(ROOT / 'content/_content.gotmpl', content / '_content.gotmpl')
    for name in ('now', 'path', 'realms', 'roots', 'about'):
        (content / (name + '.md')).write_text(
            f'---\ntitle: {name.title()}\nlastmod: 2025-01-01\n---\nFixture page.\n')
    return content


def build_site(root, layout_dir=None, data_dir=None):
    # Give each fixture a project filesystem, so fileExists sees its content,
    # including unpublished notes. Share only read-only site implementation.
    for directory in ('assets', 'data', 'layouts', 'static'):
        target = root / directory
        if not target.exists():
            target.symlink_to(ROOT / directory, target_is_directory=True)
    shutil.copyfile(ROOT / 'hugo.toml', root / 'hugo.toml')
    output = root / 'public'
    command = [os.environ.get('HUGO_BIN', str(ROOT / '.tools/bin/hugo')),
               '--source', str(root),
               '--destination', str(output), '--baseURL', BASE]
    if layout_dir:
        command.extend(['--layoutDir', str(layout_dir)])
    env = dict(os.environ)
    if data_dir:
        env['HUGO_DATADIR'] = str(data_dir)
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    return result, output
