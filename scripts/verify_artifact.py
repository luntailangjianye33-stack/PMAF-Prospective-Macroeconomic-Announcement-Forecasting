"""Verify the publication bundle's local content manifest, excluding Git metadata."""
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve()
record=json.loads((root/'ARTIFACT_MANIFEST.json').read_text(encoding='utf-8'))
files={p.relative_to(root).as_posix():p for p in root.rglob('*') if p.is_file() and '.git' not in p.relative_to(root).parts and p.name!='ARTIFACT_MANIFEST.json'}
assert set(files)=={r['path'] for r in record['files']},'file-set mismatch'
for r in record['files']:
 p=files[r['path']];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
print('PASS: '+str(len(files))+' artifact files; no public release or trusted timestamp implied.')
