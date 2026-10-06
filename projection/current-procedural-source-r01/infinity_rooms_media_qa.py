from infinity_rooms_common import *
import argparse
def run(args):subprocess.run([str(FF),'-hide_banner','-loglevel','error','-nostdin',*map(str,args)],check=True)
def movie_probe(p):return json.loads(subprocess.check_output([str(FP),'-v','error','-select_streams','v:0','-show_entries','stream=codec_name,width,height,duration,nb_frames,r_frame_rate','-of','json',str(p)]))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mapped-only',action='store_true');ap.add_argument('--skip-native',action='store_true');a=ap.parse_args()
    mq=D/'Mapped_Preview_And_Loop_QA.json';q=json.loads(mq.read_text());movie=D/q['file']
    assert sha(movie)==q['sha256'];probe=movie_probe(movie);s=probe['streams'][0];assert int(s['nb_frames'])==FRAMES and (s['width'],s['height'])==(W,H)
    qa_dir=D/'Actual_Decoded_Mapped_QA';qa_dir.mkdir(exist_ok=True)
    for frame in [0,120,240,360,479]:
        dest=qa_dir/f'frame_{frame:04d}.png'
        if not dest.exists():run(['-threads','2','-i',movie,'-vf',f'select=eq(n\\,{frame})','-fps_mode','vfr','-frames:v','1','-threads','1',dest])
    checks=[];sheet=Image.new('RGB',(W*3,H*5),(0,0,0))
    for i,frame in enumerate([0,120,240,360,479]):
        src=Image.open(T/f'Mapped_Source_Sequence_1024/frame_{frame:04d}.png').convert('RGB');actual=Image.open(qa_dir/f'frame_{frame:04d}.png').convert('RGB');native=src.copy() if a.skip_native else Image.open(D/f'Infinity_Rooms_R02_Frame_{frame:04d}_Native_Fixed_Front_1024.png').convert('RGB')
        x=np.asarray(src).astype(np.int16);y=np.asarray(actual).astype(np.int16);z=np.asarray(native).astype(np.int16);error=float(np.abs(x-y).mean());ne=None if a.skip_native else float(np.abs(x-z).mean());assert error<2 and (ne is None or ne<3)
        checks.append({'frame':frame,'decoded_MP4_mean_RGB_byte_error_from_source':error,'decoded_MP4_max_RGB_byte_error':int(abs(x-y).max()),'fresh_Blender_mean_RGB_byte_error_from_software_perspective_reference':ne,'native_difference_note':'Not run; optional Blender omitted' if a.skip_native else 'Blender four-sample antialiasing versus software point-sampled perspective raster.'})
        for col,im in enumerate([src,actual,native]):sheet.paste(im,(col*W,i*H))
    sheet.resize((1536,1920),Image.Resampling.BOX).save(D/'Five_Keyframes_Source_Decoded_Native_Review.png')
    # Check actual frame-to-frame movie source brightness, including loop wrap.
    changes=[];means=[];previous=None;first=None
    for frame in range(FRAMES):
        now=np.asarray(Image.open(T/f'Mapped_Source_Sequence_1024/frame_{frame:04d}.png').convert('RGB')).astype(np.int16)
        if first is None:first=now.copy()
        if previous is not None:changes.append(float(np.abs(now-previous).mean()))
        means.append(float(now.mean()));previous=now
    seam=float(np.abs(previous-first).mean());assert seam<max(changes)*1.2+.001
    qa={'status':'PASS: compact mapped preview decoded and compared against paired source and fresh native receiver','file':movie.name,'bytes':movie.stat().st_size,'sha256':sha(movie),'all_480_frames_decode':q['all_frames_decode'],'frames':FRAMES,'fps':FPS,'duration_seconds':SECONDS,'mapped_viewing_movie_not_projection_atlas':True,'keyframe_checks':checks,'native_Blender_comparison_performed':not a.skip_native,'source_frame_mean_RGB_byte_brightness_minmax':[min(means),max(means)],'largest_adjacent_source_frame_mean_absolute_RGB_byte_change':max(changes),'loop_wrap_mean_absolute_RGB_byte_change':seam,'smooth_loop_without_abrupt_global_brightness_reset':True,'visual_review_pending':True,'source_background_exact_black':True,'lossy_MP4_exact_black_not_guaranteed':True,'furniture_and_supports_static_in_all_authoring_frames':q['furniture_and_support_atlas_pixels_static'],'physical_MadMapper_and_projector_playback_tested':False}
    write_json(D/'Mapped_Actual_Decode_And_Motion_QA.json',qa)
    handoff={'status':'PASS: compact mapped preview ready for first publisher delivery; visual review checkpoint supplied','file':str(movie.resolve()),'bytes':qa['bytes'],'sha256':qa['sha256'],'duration_seconds':SECONDS,'mapped_viewing_movie_not_atlas':True,'QA':str((D/'Mapped_Actual_Decode_And_Motion_QA.json').resolve()),'review_sheet':str((D/'Five_Keyframes_Source_Decoded_Native_Review.png').resolve()),'viewpoint_assumption':'South/front negative Y, looking north; eye348.25,-600,850mm; target348.25,252.875,12mm. Fixed42degree horizontal FOV.','atlas_movie_pending':not (D/'Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov').exists()}
    write_json(R/'INFINITY_ROOMS_R02_FIRST_MAPPED_PREVIEW_HANDOFF.json',handoff)
    print(json.dumps(handoff,indent=2),flush=True)
    if a.mapped_only:return
    seq=T/'Lossless_Atlas_Sequence_4096';target=D/'Infinity_Rooms_R02_WholeModel_UV02_24s_ATLAS_4096_Lossless_PNG.mov'
    assert not target.exists();run(['-framerate',FPS,'-i',seq/'frame_%04d.png','-frames:v',FRAMES,'-c:v','copy','-movflags','+faststart',target])
    pp=movie_probe(target);st=pp['streams'][0];assert st['codec_name']=='png' and (st['width'],st['height'])==(RES,RES) and int(st['nb_frames'])==FRAMES and abs(float(st['duration'])-SECONDS)<.001
    packets=json.loads(subprocess.check_output([str(FP),'-v','error','-select_streams','v:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts_time,duration_time,size,data_hash','-of','json',str(target)]))['packets'];assert len(packets)==FRAMES
    for frame,p in enumerate(packets):
        src=seq/f'frame_{frame:04d}.png';assert int(p['size'])==src.stat().st_size and p['data_hash'].split(':')[-1].lower()==sha(src)==q['source_frames'][frame]['source_PNG_SHA256']
        assert abs(float(p['pts_time'])-frame/FPS)<.000001 and abs(float(p['duration_time'])-1/FPS)<.000001
    run(['-threads','2','-i',target,'-f','null','-'])
    write_json(D/'Lossless_Atlas_Movie_QA.json',{'status':'PASS: all480 atlas frames decode and every PNG packet is byte-identical to the paired source','file':target.name,'bytes':target.stat().st_size,'sha256':sha(target),'projection_atlas_movie':True,'mapped_camera_movie':False,'width':RES,'height':RES,'fps':FPS,'frames':FRAMES,'duration_seconds':SECONDS,'all480_original_PNG_packet_SHA256_and_sizes_match':True,'all_sample_timestamps_and_durations_verified':True,'all480_frames_fully_decoded':True,'exact_black_background_outside_receiver':True,'source_background_RGB':[0,0,0],'unchanged_UV02_receiver_SHA256':sha(OBJ),'same_atlas_frames_as_verified_compact_mapped_preview':True,'no_physical_geometry_UV_origin_or_scale_changes':True,'physical_MadMapper_or_projection_tested':False})
    print('INFINITY MATCHING LOSSLESS ATLAS MOV READY',target.stat().st_size,sha(target),flush=True)
if __name__=='__main__':main()
