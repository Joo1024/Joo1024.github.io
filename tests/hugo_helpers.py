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
    output = root / 'public'
    command = [os.environ.get('HUGO_BIN', str(ROOT / '.tools/bin/hugo')),
               '--source', str(ROOT), '--contentDir', str(root / 'content'),
               '--destination', str(output), '--baseURL', BASE]
    if layout_dir:
        command.extend(['--layoutDir', str(layout_dir)])
    env = dict(os.environ)
    if data_dir:
        env['HUGO_DATADIR'] = str(data_dir)
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    return result, output
