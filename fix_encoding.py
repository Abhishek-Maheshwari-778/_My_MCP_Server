"""Fix Windows UTF-8 encoding for all project Python files."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from pathlib import Path

PATCH = 'import sys, io\nsys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")\n'

targets = (
    list(Path('src').glob('*.py')) +
    list(Path('mcp_server').glob('*.py')) +
    [Path('main.py'), Path('watcher.py'), Path('agent.py'), Path('config.py')]
)

for f in targets:
    if not f.exists():
        continue
    try:
        text = f.read_text(encoding='utf-8')
        if 'sys.stdout = io.TextIOWrapper' in text:
            print(f'  [skip] already patched: {f}')
            continue
        # insert patch right after first occurrence of "import sys"
        if 'import sys\n' in text:
            text = text.replace('import sys\n', 'import sys\n' + PATCH, 1)
        elif text.startswith('"""'):
            # insert after docstring block
            idx = text.find('"""', 3) + 3
            text = text[:idx] + '\n' + PATCH + text[idx:]
        else:
            text = PATCH + text
        f.write_text(text, encoding='utf-8')
        print(f'  [OK] patched: {f}')
    except Exception as e:
        print(f'  [ERR] {f}: {e}')

print('\nAll files patched.')
