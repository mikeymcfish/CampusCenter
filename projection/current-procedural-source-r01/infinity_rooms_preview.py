from infinity_rooms_common import *
import argparse,concurrent.futures,time
S=T/'Lossless_Atlas_Sequence_4096';MS=T/'Mapped_Source_Sequence_1024';S.mkdir(exist_ok=True);MS.mkdir(exist_ok=True)
KEYS=[0,120,240,360,479]
def init():
    global effect
    effect=Effect()
def work(frame):
    atlas=effect.render(frame);png=S/f'frame_{frame:04d}.png'
    Image.fromarray(atlas).save(png,compress_level=2)
    im=effect.mapped(atlas);im.save(MS/f'frame_{frame:04d}.png',compress_level=1)
    if frame in KEYS:
        key=D/f'Infinity_Rooms_R02_Frame_{frame:04d}_Lossless_Atlas_4096.png'
        if key.exists():assert np.array_equal(np.asarray(Image.open(key)),atlas)
        else:Image.fromarray(atlas).save(key,compress_level=2)
        key=D/f'Infinity_Rooms_R02_Frame_{frame:04d}_Fixed_Front_Mapped_1024.png'
        if not key.exists():im.save(key)
    return frame,im.tobytes(),sha(png)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');a=ap.parse_args()
    if a.stills:
        init()
        start=effect.render(0);end=effect.render(FRAMES);assert np.array_equal(start,end)
        for frame in KEYS:work(frame);print('INFINITY KEYFRAME READY',frame,flush=True)
        write_json(D/'Initial_Keyframe_And_Loop_QA.json',{'status':'PASS','receiver_SHA256':sha(OBJ),'frame0_equals_virtual_terminal_frame480':True,'fixed_physical_geometry_and_fixed_fixture_atlas_pixels':True,'viewpoint':EYE.tolist(),'target':TARGET.tolist(),'resolution':[RES,RES],'preview_resolution':[W,H],'whole_model_scope':True,'physical_projection_or_MadMapper_playback_tested':False})
        return
    target=D/'Infinity_Rooms_R02_WholeModel_UV02_24s_Fixed_Front_Mapped_1024_Viewing.mp4';assert not target.exists()
    cmd=[str(FF),'-hide_banner','-loglevel','error','-nostdin','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','16','-threads','8','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
    rows=[];started=time.monotonic()
    with (T/'Mapped_Encode_Log.txt').open('wb') as log,concurrent.futures.ProcessPoolExecutor(max_workers=4,initializer=init) as pool:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for frame,blob,h in pool.map(work,range(FRAMES),chunksize=1):
            proc.stdin.write(blob);rows.append({'frame':frame,'source_PNG_SHA256':h})
            if frame%60==0:print('INFINITY MAPPED LOOP',frame,'/',FRAMES,flush=True)
        proc.stdin.close();assert proc.wait()==0
    subprocess.run([str(FF),'-hide_banner','-loglevel','error','-nostdin','-threads','2','-i',str(target),'-f','null','-'],check=True)
    probe=json.loads(subprocess.check_output([str(FP),'-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,duration,nb_frames,r_frame_rate','-of','json',str(target)]))
    st=probe['streams'][0];assert int(st['nb_frames'])==FRAMES and abs(float(st['duration'])-SECONDS)<.001
    init();assert np.array_equal(effect.render(0),effect.render(FRAMES))
    qa={'status':'PASS: compact mapped authoring, full decode and continuous virtual loop; visual/native checks pending','file':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'mapped_camera_viewing_movie':True,'projection_atlas_movie':False,'resolution':[W,H],'fps':FPS,'frames':FRAMES,'duration_seconds':SECONDS,'all_frames_decode':True,'frame0_equals_virtual_terminal_frame480':True,'last_frame_is_one_normal_time_step_before_first':True,'fixed_front_eye_mm':EYE.tolist(),'fixed_front_target_mm':TARGET.tolist(),'original_UV02_receiver_SHA256':sha(OBJ),'no_physical_mesh_or_UV_deformation':True,'furniture_and_support_atlas_pixels_static':True,'paired_lossless_atlas_sequence_available':True,'source_frames':rows,'render_and_encode_seconds':time.monotonic()-started,'visual_review_pending':True,'native_Blender_validation_pending':True,'physical_projection_or_MadMapper_playback_tested':False,'probe':probe}
    write_json(D/'Mapped_Preview_And_Loop_QA.json',qa)
    print(json.dumps({k:qa[k] for k in ['status','file','bytes','sha256','render_and_encode_seconds']},indent=2),flush=True)
if __name__=='__main__':main()
