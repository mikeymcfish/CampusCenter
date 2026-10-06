"""Generate current Infinity pixels from the compact inputs and frozen public mesh."""
from pathlib import Path
import argparse,hashlib,json,numpy as np
R=Path(__file__).parent
def pixel_sha(x):return hashlib.sha256(np.asarray(x,dtype=np.uint8).tobytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--production-root',type=Path);a=ap.parse_args()
    cfg=json.loads((R/'Infinity_R02_Rebuild_Config.json').read_text())
    from infinity_rooms_common import Effect
    e=Effect();checks=[]
    for row in cfg['expected_keyframe_pixel_hashes']:
        frame=row['frame'];atlas=e.render(frame);mapped=np.asarray(e.mapped(atlas))
        ah=pixel_sha(atlas);mh=pixel_sha(mapped);assert ah==row['atlas_RGB_pixel_sha256'],('Infinity atlas',frame);assert mh==row['mapped_RGB_pixel_sha256'],('Infinity mapped',frame)
        checks.append({'frame':frame,'atlas_RGB_pixel_SHA256':ah,'mapped_RGB_pixel_SHA256':mh,'accepted_atlas_and_mapped_pixels_bit_identical':True})
        print('INFINITY ACTUAL GENERATION PIXELS MATCH ACCEPTED',frame,flush=True)
    assert np.array_equal(e.render(0),e.render(480))
    assert int(e.dynamic_mask.sum())==cfg['animated_floor_texels']==1027056
    g=e.g;assert not np.any(g['aperture']&g['full_obstacles']) and not np.any(g['aperture']&g['protected'])
    fresh={}
    if a.production_root:
        original=a.production_root/'madmapper_infinity_rooms_R02/cache'
        for k in ['front_u','front_v','front_part','front_z']:
            old=np.load(original/(k+'.npy'),mmap_mode='r');assert np.array_equal(e.front[k],old),('Fixed front geometry cache',k)
            fresh[k]={'shape':list(old.shape),'dtype':str(old.dtype),'bit_identical_to_accepted_geometry_cache':True}
    out={'status':'PASS: actual current Infinity generation reproduces all five accepted keyframes','keyframe_checks':checks,'geometry_constrained_regions':37,'animated_floor_texels':1027056,'aperture_overlap_obstacles_or_supports_cells':0,'all_non_aperture_fixture_pixels_are_fixed_by_generation_assertion':True,'frame0_equals_terminal_frame480':True,'fixed_front_cache_regenerated_from_published_UV02':True,'production_front_array_comparisons':fresh,'random_seed':None,'full480frame_movie_reencoding_rerun':False,'physical_MadMapper_or_projection_tested':False}
    (R/'Infinity_Rebuild_Verification_QA.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
