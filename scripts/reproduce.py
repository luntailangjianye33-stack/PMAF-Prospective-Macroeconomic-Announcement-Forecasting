"""Offline reproduction of both QB formats from the publication bundle."""
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(expected,actual):
    generated={p.relative_to(actual).as_posix():sha(p) for p in actual.rglob('*') if p.is_file()}
    errors=[name for name,digest in generated.items() if not (expected/name).is_file() or sha(expected/name)!=digest]
    assert not errors,errors
    return len(generated)
def main(root):
    binary=root/'banks/binary';point=root/'banks/point'
    with tempfile.TemporaryDirectory(prefix='pmaf_dual_replay_') as temp:
        t=Path(temp);inp=t/'inputs';inp.mkdir();shutil.copy2(binary/'management/build_input_config.json',inp/'config.json');shutil.copytree(binary/'management/raw',inp/'raw')
        subprocess.run([sys.executable,'-B',str(binary/'scripts/build.py'),'--inputs',str(inp),'--out',str(t/'binary')],check=True,capture_output=True)
        nb=compare(binary,t/'binary')
        subprocess.run([sys.executable,'-B',str(point/'scripts/build_point.py'),'--binary',str(binary),'--settings',str(point/'global/point_settings.json'),'--out',str(t/'point')],check=True,capture_output=True)
        np=compare(point,t/'point')
    return {'status':'PASS','binary_generated_files_identical':nb,'point_generated_files_identical':np,'network':False,'comparison':'every build-produced file against packaged counterpart; post-build validation/seal supplements verified by manifests'}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();print(json.dumps(main(a.root.resolve()),indent=2))
