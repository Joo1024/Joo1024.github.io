#!/usr/bin/env bash
# Install the same verified, dependency-free Hugo binary locally and in CI.
set -euo pipefail

HUGO_VERSION=0.147.9
repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
install_dir=${HUGO_INSTALL_DIR:-"$repo_root/.tools/bin"}
mkdir -p "$install_dir"

if [ -x "$install_dir/hugo" ]; then
  installed_version=$("$install_dir/hugo" version)
  case "$installed_version" in
    "hugo v${HUGO_VERSION}-"*) printf '%s\n' "$installed_version"; exit 0 ;;
  esac
fi

case "$(uname -s)/$(uname -m)" in
  Linux/x86_64) platform=linux-amd64 ;;
  Linux/aarch64|Linux/arm64) platform=linux-arm64 ;;
  Darwin/x86_64|Darwin/arm64) platform=darwin-universal ;;
  *) echo 'Use the official Hugo 0.147.9 installation for your platform.' >&2; exit 1 ;;
esac

archive="hugo_${HUGO_VERSION}_${platform}.tar.gz"
release="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}"
download_dir=$(mktemp -d)
trap 'rm -rf "$download_dir"' EXIT
curl --fail --silent --show-error --location --retry 2 "$release/$archive" -o "$download_dir/$archive"
curl --fail --silent --show-error --location --retry 2 "$release/hugo_${HUGO_VERSION}_checksums.txt" -o "$download_dir/checksums.txt"
python3 - "$download_dir" "$archive" <<'PY'
from pathlib import Path
import hashlib
import sys

root = Path(sys.argv[1])
name = sys.argv[2]
matches = [line.split()[0] for line in (root / 'checksums.txt').read_text().splitlines()
           if line.split()[-1] == name]
if len(matches) != 1 or hashlib.sha256((root / name).read_bytes()).hexdigest() != matches[0]:
    sys.exit('Hugo archive checksum verification failed.')
print(f'Verified official SHA256: {name}')
PY
tar -xzf "$download_dir/$archive" -C "$install_dir" hugo
"$install_dir/hugo" version
