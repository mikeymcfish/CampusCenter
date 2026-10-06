"""Run current accepted generation stages in a new workspace; never installs tools."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,os,numpy as np
BUNDLE=Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def equal_npz(old,new):
    with np.load(old,allow_pickle=False) as a,np.load(new,allow_pickle=False) as b:
        assert set(a.files)==set(b.files),(old,'keys')
        for key in a.files:assert np.array_equal(a[key],b[key]),(old,key,'Regenerated geometry input differs from accepted reference; stop before rendering')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--workdir',type=Path,required=True);ap.add_argument('--download',action='store_true');ap.add_argument('--repo',type=Path);ap.add_argument('--receiver-zip',type=Path)
    ap.add_argument('--revision',choices=['r03','r04','infinity','all'],default='all');ap.add_argument('--prepare-only',action='store_true')
    ap.add_argument('--regenerate-native-domains',action='store_true');ap.add_argument('--regenerate-infinity-apertures',action='store_true')
    ap.add_argument('--ffmpeg');ap.add_argument('--ffprobe');ap.add_argument('--blender');a=ap.parse_args()
    work=a.workdir.resolve();assert work!=BUNDLE.resolve(),'Choose a separate workspace';assert not work.exists() or not any(work.iterdir()),'Workdir must be new or empty; existing results are preserved'
    work.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((BUNDLE/'Bundle_File_SHA256.json').read_text())
    for row in manifest['files']:
        src=(BUNDLE/row['file']).resolve();target=(work/row['file']).resolve();assert src.is_relative_to(BUNDLE.resolve()) and target.is_relative_to(work)
        assert src.is_file() and src.stat().st_size==row['bytes'] and sha(src)==row['sha256'],('Source/input hash mismatch',row['file'])
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
    shutil.copyfile(BUNDLE/'Bundle_File_SHA256.json',work/'Bundle_File_SHA256.json')
    if a.ffmpeg:os.environ['FFMPEG']=a.ffmpeg
    if a.ffprobe:os.environ['FFPROBE']=a.ffprobe
    os.environ.pop('RIPPLE_R04_FIELD_ROOT',None)
    def run(script,*args):subprocess.run([sys.executable,str(work/script),*map(str,args)],cwd=work,check=True)
    resolve=[]
    if a.download:resolve.append('--download')
    if a.repo:resolve.extend(['--repo',a.repo.resolve()])
    if a.receiver_zip:resolve.extend(['--receiver-zip',a.receiver_zip.resolve()])
    run('resolve_public_inputs.py',*resolve);run('verify_source_bundle.py')
    if a.prepare_only:
        print('PREPARATION PASS:',work,'Exact code/compact inputs and published receivers resolved; no simulation or encoding run.',flush=True);return
    if a.regenerate_native_domains:
        run('ripple_r02_domains.py','--whole-model');run('ripple_whole_fixture_volume_audit.py','--connected')
        for row in json.loads((BUNDLE/'Locked_Domain_Input_SHA256.json').read_text())['inputs']:equal_npz(BUNDLE/row['file'],work/row['file'])
        equal_npz(BUNDLE/'madmapper_ripple_R03/whole_model/Whole_Native_Obstacle_And_Ownership_Grid.npz',work/'madmapper_ripple_R03/whole_model/Whole_Native_Obstacle_And_Ownership_Grid.npz')
    if a.revision in ['r03','r04','all']:
        (work/'madmapper_ripple_R03/whole_model/deliverables').mkdir(exist_ok=True)
        (work/'madmapper_ripple_R04/whole_model/deliverables').mkdir(parents=True,exist_ok=True)
        (work/'madmapper_ripple_R04/whole_model/Lossless_Atlas_Sequence_4096').mkdir(exist_ok=True)
        if a.revision=='r03':run('ripple_r03_connected_solver.py');run('ripple_r03_connected_transfer.py');run('ripple_r03_mapped_decode_preview.py')
        else:
            run('ripple_r04_staggered_solver.py');run('ripple_r04_parallel_preview.py');run('ripple_r04_compact_black_decode_qa.py');run('ripple_r04_lossless_atlas_movie.py');run('ripple_r04_exact_black_mapped_reference.py');run('ripple_r04_actual_crest_width_qa.py')
            if a.blender:subprocess.run([a.blender,'--background','--factory-startup','--disable-autoexec','--threads','8','--python-exit-code','1','--python',str(work/'hybrid_media_native_preview.py'),'--','--folder','madmapper_ripple_R04/whole_model/deliverables','--pattern','*_Lossless_Atlas_4096.png','--black-background'],cwd=work,check=True)
    if a.revision in ['infinity','all']:
        if a.regenerate_infinity_apertures:
            run('production_navigation.py');run('infinity_rooms_preflight.py')
            equal_npz(BUNDLE/'madmapper_infinity_rooms_R02/cache/Infinity_Room_Apertures_And_Depth.npz',work/'madmapper_infinity_rooms_R02/cache/Infinity_Room_Apertures_And_Depth.npz')
        run('infinity_rooms_preview.py')
        if a.blender:subprocess.run([a.blender,'--background','--factory-startup','--disable-autoexec','--threads','8','--python-exit-code','1','--python',str(work/'infinity_rooms_native_preview.py')],cwd=work,check=True)
        run('infinity_rooms_media_qa.py',*([] if a.blender else ['--skip-native']))
    print('REBUILD STAGES COMPLETE:',work,'Compare decoded pixels and QA; encoded-file hashes may differ by encoder/library versions.',flush=True)
if __name__=='__main__':main()
