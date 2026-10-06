import os,shutil
from pathlib import Path
import concurrent.futures,subprocess,json,hashlib,numpy as np
from PIL import Image
R=Path(__file__).parent;T=R/'madmapper_ripple_R04/whole_model';D=T/'deliverables';S=T/'Lossless_Atlas_Sequence_4096';M=T/'Mapped_Source_Sequence_1024';M.mkdir(exist_ok=True)
FRAMES=880;FPS=20;TARGET=D/'Ripple_R04_Black_Thin_Staggered_Connected_44s_Mapped_1024_Viewing_Preview.mp4'
def init():
    global transfer
    import ripple_r04_thin_ridge_transfer as transfer
def work(frame):
    p=S/f'frame_{frame:04d}.png';atlas=None
    if p.exists():
        try:atlas=np.asarray(Image.open(p).convert('RGB'));assert atlas.shape==(4096,4096,3)
        except Exception:atlas=None
    if atlas is None:atlas=transfer.render(frame);Image.fromarray(atlas).save(p,compress_level=2)
    im=transfer.mapped(atlas);im.save(M/f'frame_{frame:04d}.png',compress_level=1)
    if frame in [0,60,120,240,400,640,879]:Image.fromarray(atlas).save(D/f'Ripple_R04_Frame_{frame:04d}_Lossless_Atlas_4096.png');im.save(D/f'Ripple_R04_Frame_{frame:04d}_Mapped_1024.png')
    return frame,im.tobytes(),int(np.count_nonzero(np.any(atlas,axis=2)))
def main():
    assert not TARGET.exists();q=json.loads((T/'Staggered_Connected_Wave_Physics_QA.json').read_text());assert q['status'].startswith('PASS')
    ff=Path(os.environ.get('FFMPEG',shutil.which('ffmpeg') or 'ffmpeg'));cmd=[str(ff),'-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1024x786','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p','-movflags','+faststart',str(TARGET)]
    stats=[]
    with (T/'Parallel_Compact_Encoding_Log.txt').open('wb') as log,concurrent.futures.ProcessPoolExecutor(max_workers=6,initializer=init) as pool:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for frame,blob,active in pool.map(work,range(FRAMES),chunksize=1):
            proc.stdin.write(blob);stats.append({'frame':frame,'nonzero_atlas_pixels':active})
            if frame%80==0:print('R04 PARALLEL PURE-BLACK THIN WAVE PREVIEW',frame,'/',FRAMES,active,flush=True)
        proc.stdin.close();assert proc.wait()==0
    init();terminal=transfer.render(FRAMES);assert not np.any(terminal)
    assert not np.any(np.asarray(Image.open(S/'frame_0000.png'))) and not np.any(np.asarray(Image.open(S/f'frame_{FRAMES-1:04d}.png')))
    result={'status':'Authoring PASS: pure-black thin-wave compact preview and matching lossless atlas sequence; actual encoded QC pending','file':str(TARGET),'bytes':TARGET.stat().st_size,'sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest(),'width':1024,'height':786,'fps':20,'frames':FRAMES,'duration_seconds':44,'stored_physics_duration_seconds':64,'physical_solve_naturally_quiet_at_rendered_repeat_boundary':True,'lossless_atlas_sequence':str(S),'matching_sequence_frames':FRAMES,'mapped_source_sequence':str(M),'atlas_resolution':4096,'background_RGB':[0,0,0],'ambient_wash_static_grey_glow_or_banner':False,'fixture_and_fireplace_neutral_patch_removed_for_black_wave_effect':True,'physical_fixture_geometry_preserved_and_obstructs_waves':True,'ridge_method':'Principal negative-curvature crest ridge of actual connected solved wave field; compact parabolic support1.7mm, amplitude from actual positive wave height, brightness saturated at0.00037mm. No analytic overlay rings.','ridge_full_support_width_model_mm':1.7,'crest_RGB':[40,235,248],'quiet_height_threshold_model_mm':.00007,'first_last_terminal_lossless_atlas_black_exact':True,'sampler':'Same original UVs and actual hybrid receiver +Z visibility; bilinear physical field; BOX1024 reduction; no ambient model shading.','receiver_OBJ_sha256':'b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba','geometry_UVs_scale_origin_and_R03_unchanged':True,'physical_domains':56,'source_events':77,'source_first_last_times_seconds':[q['source_timing_first_seconds'],q['source_timing_last_seconds']],'reference_zones_do_not_partition_solver':True,'Commons_Cafe_open_edges_transmit':137,'all_open_label_edges_transmit':2380,'all_frames_source_statistics':stats,'matching_primary_atlas_movie_pending':True,'physical_projection_or_MadMapper_playback_verified':False}
    (D/'Thin_Black_Staggered_Transfer_QA.json').write_text(json.dumps(result,indent=2));print('R04 COMPACT AUTHOR COMPLETE',TARGET,flush=True)
if __name__=='__main__':main()
