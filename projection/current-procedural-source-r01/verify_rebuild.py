"""Verify compact inputs and numerical code; optional read-only production comparison."""
from pathlib import Path
import argparse,ast,json,hashlib,collections,sys,os,importlib,numpy as np
R=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--production-root',type=Path);ap.add_argument('--build-caches',action='store_true');a=ap.parse_args();checks={}
    for name in ['Native_Geometry_Input_SHA256.json','Locked_Domain_Input_SHA256.json']:
        data=json.loads((R/name).read_text());missing=[]
        for row in data['inputs']:
            p=R/row['file'];assert p.is_file(),row['file'];assert sha(p)==row['sha256'],row['file']
            if p.suffix=='.npz':
                z=np.load(p,allow_pickle=False);assert all(z[k].dtype.kind!='O' for k in z.files)
        checks[name]={'count':data['count'],'all_files_and_SHA256_match':True,'object_pickle_arrays':False}
    for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
    assert not list(R.rglob('*_Height_Sequence.npy')),'Verification expects no bundled/generated height caches'
    production=R/'ripple_r04_staggered_solver.py';prefix=production.read_text().split('fields={',1)[0];namespace={'__file__':str(production),'__name__':'numeric_verification'};exec(compile(prefix,str(production),'exec'),namespace)
    accepted=json.loads((R/'Evidence/R04/Staggered_Connected_Wave_Physics_QA.json').read_text());actual=[]
    for row in namespace['components']:
        for e in row['source_events']:actual.append({'component':row['name'],'reference_owner':e['reference_owner'],'point_model_mm':e['point'].tolist(),'time_seconds':e['time']})
    expected=[{'component':row['name'],**e} for row in accepted['components'] for e in row['source_events']];assert actual==expected and len(actual)==77
    checks['source_schedule']={'events':77,'actual_production_rule_reexecuted':True,'matches_all_accepted_points_owners_components_and_times_exactly':True,'random_seed':None}
    from ripple_r02_solver import behaviour_tests
    checks['synthetic_reflection_and_isolation']=behaviour_tests()
    gym=next(row for row in namespace['components'] if any(e['reference_owner']==999 for e in row['source_events']));b=gym['b'];events=gym['source_events']
    for frame in range(1,61):
        for sub in range(4):
            t=(frame-1)/20+sub*.0125
            for e in events:
                if not e['applied'] and t<=e['time']<t+.0125:b.impulse(e['point']);e['applied']=True
            b.step()
    checks['short_real_Gym_solve']={'component':gym['name'],'seconds':3,'substeps':240,'height_nonzero':bool(np.any(b.h)),'finite':bool(np.isfinite(b.h).all()),'float32_state_SHA256':hashlib.sha256(b.h.astype(np.float32).tobytes()).hexdigest()};assert checks['short_real_Gym_solve']['finite']
    assert checks['short_real_Gym_solve']['float32_state_SHA256']=='ca09f6abf5acc5d2e4371fcefb644ca3294a07b107e3184d92c542fb9b69aa59','Short Gym solve differs from retained production state'
    if a.production_root:
        old=np.load(a.production_root/'madmapper_ripple_R04/whole_model'/(gym['name']+'_Height_Sequence.npy'),mmap_mode='r')[60];assert np.array_equal(old,b.h.astype(np.float32));checks['short_real_Gym_solve']['accepted_production_frame60_float32_bit_identical']=True
    if a.build_caches:
        from production_common import cache_arrays
        arrays=cache_arrays(100,4096);checks['world_cache']={'rebuilt_from_published_exact_UV01':True,'arrays':{}}
        for key in arrays:
            if a.production_root:
                original=np.load(a.production_root/'madmapper_production_P01/cache/assembly_1_100_4096_world64'/(key+'.npy'),mmap_mode='r');assert np.array_equal(arrays[key],original),key
            checks['world_cache']['arrays'][key]={'shape':list(arrays[key].shape),'dtype':str(arrays[key].dtype),'accepted_production_array_exact_match':bool(a.production_root)}
        from hybrid_projection_cache import load
        top=load();checks['hybrid_top_cache']={'rebuilt_from_published_exact_UV01_and_UV02':True,'arrays':{}}
        for key,value in top.items():
            if a.production_root:
                original=np.load(a.production_root/'madmapper_hybrid_UV02/cache/top'/(key+'.npy'));assert np.array_equal(value,original),('Hybrid top cache',key)
            checks['hybrid_top_cache']['arrays'][key]={'shape':list(value.shape),'dtype':str(value.dtype),'accepted_production_array_exact_match':bool(a.production_root)}
        if a.production_root:
            os.environ['RIPPLE_R04_FIELD_ROOT']=str(a.production_root/'madmapper_ripple_R04/whole_model');transfer=importlib.import_module('ripple_r04_thin_ridge_transfer');from PIL import Image
            keys=[]
            for frame in [0,60,120,240,400,640,879]:
                current=transfer.render(frame);original=np.asarray(Image.open(a.production_root/'madmapper_ripple_R04/whole_model/deliverables'/f'Ripple_R04_Frame_{frame:04d}_Lossless_Atlas_4096.png').convert('RGB'));assert np.array_equal(current,original),('Atlas differs',frame)
                mapped=np.asarray(transfer.mapped(current));oldmapped=np.asarray(Image.open(a.production_root/'madmapper_ripple_R04/whole_model/Mapped_Source_Sequence_1024'/f'frame_{frame:04d}.png').convert('RGB'));assert np.array_equal(mapped,oldmapped),('Mapped differs',frame);keys.append({'frame':frame,'raw_atlas_pixels_identical':True,'mapped_pixels_identical':True});print('PORTABLE REBUILD R04 ACCEPTED KEYFRAME PIXELS MATCH',frame,flush=True)
            checks['accepted_R04_transfer_keyframes']=keys
    out={'status':'PASS: source/input resolution, exact timing and numerical smoke checks','checks':checks,'full64second_simulation_rerun':False,'full880frame_movie_encoding_rerun':False,'physical_projection_or_MadMapper_playback_verified':False};(R/'Rebuild_Verification_QA.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
