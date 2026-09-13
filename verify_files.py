"""SHA-256 integrity check using only Python's standard library."""
import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'SHA256SUMS'
EXCLUDED_DIRS = {'.git', 'build', '__pycache__', '.venv'}


def included_files():
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or path == MANIFEST:
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.suffix in {'.log', '.pyc', '.FCBak', '.FCStd1', '.zip'} or path.name == '.env':
            continue
        yield path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Regenerate manifest after intentional changes.')
    args = parser.parse_args()
    if args.write:
        lines = [hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.relative_to(ROOT).as_posix()
                 for path in included_files()]
        MANIFEST.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        print(f'SHA256SUMS written: {len(lines)} files')
        return
    if not MANIFEST.exists():
        raise SystemExit('FAIL: SHA256SUMS missing')
    failures = []
    seen = set()
    for line in MANIFEST.read_text(encoding='utf-8').splitlines():
        try:
            expected, name = line.split('  ', 1)
        except ValueError:
            failures.append('Malformed manifest line')
            continue
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or name in seen:
            failures.append('Invalid or duplicate path: ' + name)
            continue
        seen.add(name)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append('Missing or changed: ' + name)
    actual = {p.relative_to(ROOT).as_posix() for p in included_files()}
    failures.extend('Not in manifest: ' + name for name in sorted(actual - seen))
    if failures:
        raise SystemExit('\n'.join(['FAIL'] + failures))
    if not seen:
        raise SystemExit('FAIL: empty manifest')
    print(f'PASS: {len(seen)} files match SHA256SUMS. No CAD or physical test performed by this command.')


if __name__ == '__main__':
    main()
