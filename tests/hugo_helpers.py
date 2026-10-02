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
    return content


def build_site(root, layout_dir=None):
    output = root / 'public'
    command = [os.environ.get('HUGO_BIN', str(ROOT / '.tools/bin/hugo')),
               '--source', str(ROOT), '--contentDir', str(root / 'content'),
               '--destination', str(output), '--baseURL', BASE]
    if layout_dir:
        command.extend(['--layoutDir', str(layout_dir)])
    result = subprocess.run(command, capture_output=True, text=True)
    return result, output
