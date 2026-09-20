"""Verify local content seal. This is not a trusted timestamp verification."""
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]);m=json.loads((root/'manifest.json').read_text(encoding='utf-8'));f=json.loads((root/'freeze.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(root/'manifest.json')==f['manifest_sha256'],'manifest digest mismatch'
expected={x['path'] for x in m['files']}
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.name not in ['manifest.json','freeze.json']}
assert actual==expected,('file set mismatch',actual^expected)
for r in m['files']:
 p=root/r['path'];assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],r['path']
print('PASS: '+str(len(expected))+' files; local seal integrity only.')
