"""Build a portable, English-only, source-inclusive Grok Bot MCP archive."""
import hashlib
import json
from pathlib import Path
import re
import zipfile

root = Path(__file__).resolve().parent.parent
version = json.loads((root / 'package.json').read_text())['version']
release = root / 'release'
release.mkdir(exist_ok=True)
archive = release / f'noesis-grok-bot-{version}.zip'
files = [root / name for name in (
    'LICENSE', 'README.md', 'GROK_BOT.md', 'THIRD_PARTY_NOTICES.md',
    'package.json', 'package-lock.json', 'dist/server.cjs',
)]
for directory in ('src', 'scripts', 'tests', 'skills', 'docs'):
    files.extend(p for p in (root / directory).rglob('*') if p.is_file() and p.suffix in ('.mjs', '.md', '.json', '.py'))
files = sorted(set(files))
han = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]')
checksums = {}
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise RuntimeError(f'Invalid release path: {path}')
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        content = data.decode('utf-8')
        if path.suffix == '.json':
            content = json.dumps(json.loads(content), ensure_ascii=False)
        if han.search(content):
            raise RuntimeError(f'Non-English CJK content: {relative}')
        output.writestr('noesis-grok-bot/' + relative, data)
        checksums[relative] = hashlib.sha256(data).hexdigest()
    output.writestr('noesis-grok-bot/SHA256SUMS.json', json.dumps(checksums, indent=2) + '\n')
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(release / (archive.name + '.sha256')).write_text(f'{digest}  {archive.name}\n')
print(json.dumps({'archive': str(archive), 'files': len(files), 'sha256': digest}))
