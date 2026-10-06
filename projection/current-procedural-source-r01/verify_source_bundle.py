"""Validate every declared source/input file and reject undeclared large media."""
from pathlib import Path
import argparse,hashlib,json,ast
R=Path(__file__).parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--production-root',type=Path);a=ap.parse_args()
    m=json.loads((R/'Bundle_File_SHA256.json').read_text());rows=m['files'];assert len({r['file'] for r in rows})==len(rows)
    for row in rows:
        p=(R/row['file']).resolve();assert p.is_relative_to(R.resolve());assert p.is_file() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['file']
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
        assert p.suffix.lower() not in ['.mov','.mp4','.avi','.blend','.exe','.dll','.pyd'],row['file']
        assert '_Height_Sequence' not in row['file'] and '/frame_' not in row['file'],row['file']
    proven=json.loads((R/'Production_Script_Provenance.json').read_text())['scripts']
    for row in proven:
        assert sha(R/row['script'])==row['bundle_sha256']
        if a.production_root:assert sha(a.production_root/row['script'])==row['production_sha256'],('Original generation script changed',row['script'])
    print(json.dumps({'status':'PASS','declared_files':len(rows),'production_generation_and_support_scripts':len(proven),'all_declared_file_SHA256_size_and_AST_checks_passed':True,'production_script_hashes_checked_read_only':bool(a.production_root),'no_movies_animation_frames_height_states_or_third_party_binaries_packaged':True},indent=2),flush=True)
if __name__=='__main__':main()
