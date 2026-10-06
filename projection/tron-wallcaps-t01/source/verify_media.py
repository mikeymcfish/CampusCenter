"""Read-only decoded-media QA and hash manifest for this isolated delivery."""
from inspect_receiver import *
from build_test import S,FPS,DURATION,OUT,CACHE,QA,FFMPEG,colours,mapped,make_atlas
from PIL import Image
import subprocess,time

def probe(p):
    ff=FFMPEG.with_name('ffprobe.exe')
    return json.loads(subprocess.check_output([str(ff),'-v','error','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_frames,duration','-show_entries','format=duration,size','-of','json',str(p)],text=True))

def main():
    q=dict(np.load(CACHE/'effect_samples.npz'));forbid=np.load(CACHE/'forbidden.npy',mmap_mode='r');files={p.name:probe(p) for p in OUT.glob('*') if p.suffix in ['.mov','.mp4']}
    for name,meta in files.items():
        st=meta['streams'][0];wh=(S,S) if name.endswith('.mov') else (1024,786)
        assert (st['width'],st['height'])==wh
        assert st['r_frame_rate']=='24/1' and int(st['nb_frames'])==240 and abs(float(st['duration'])-10)<1e-6
        if name.endswith('.mov'):assert st['codec_name']=='qtrle' and st['pix_fmt']=='rgb24'
    movie=OUT/'Tron_WallCaps_UV02_Atlas_8192_10s24_Lossless.mov';checks=[]
    # Decode actual media pixels at representative frames, including endpoints.
    for i in [0,60,120,180,239]:
        cmd=[str(FFMPEG),'-v','error','-ss',f'{i/FPS:.9f}','-i',str(movie),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1']
        data=subprocess.check_output(cmd);assert len(data)==S*S*3
        arr=np.frombuffer(data,dtype=np.uint8).reshape(S*S,3)
        exp=colours(q,i/FPS);err=int(np.abs(arr[q['flat']].astype(int)-exp.astype(int)).max())
        excludedmax=int(arr.reshape(S,S,3)[forbid].max(initial=0))
        off=np.ones(S*S,bool);off[q['flat']]=False;outmax=int(arr[off].max(initial=0))
        checks.append({'decoded_frame':i,'source_rgb_max_difference':err,'excluded_texel_max_RGB':excludedmax,'outside_effect_max_RGB':outmax})
        assert err==0 and excludedmax==0 and outmax==0
        if i==239:Image.fromarray(mapped(arr.reshape(S,S,3))).save(QA/'Decoded_Last_Frame_Mapped_1024.png')
        print('DECODED QA',i,checks[-1],flush=True)
    # Quantify visible motion over one frame intervals, including wrap.
    views=[mapped(make_atlas(q,i/FPS)) for i in [0,1,60,120,180,239]]
    differences=[]
    for j,k in [(0,1),(0,2),(0,3),(0,4),(5,0)]:
        delta=np.abs(views[j].astype(int)-views[k].astype(int));differences.append({'frames':[[0,1,60,120,180,239][j],[0,1,60,120,180,239][k]],'changed_pixels_over_RGB_4':int((delta.max(2)>4).sum()),'RGB_max_delta':int(delta.max()),'RGB_mean_delta_over_selected_pixels':float(delta[views[j].max(2)>10].mean())})
    assert sha(OBJ)=='b949784cbb3f833d10d82fdd48d469ac3fac1b8ac723f7cc08588ca633a59fba'
    assert sha(ORIGINAL_SRC/OBJ.name)==sha(OBJ)
    assert sha(ROOT/'receiver_copy'/OBJ.name)==sha(OBJ)
    sourcecopies={name:sha(ORIGINAL_SRC/name)==sha(SRC/name) for name in [OBJ.name,'CampusCenter_P02_Assembly_1_100_UV01.mtl','Atlas_Diagnostic.png']};assert all(sourcecopies.values())
    qa={'status':'PASS','decoded_lossless_media_checks':checks,'video_streams':files,'motion_pixel_evidence':differences,'mathematical_0_vs_10_loop_max_RGB_error':int(np.abs(colours(q,0).astype(int)-colours(q,10).astype(int)).max()),'receiver_source_sha256_unchanged':sha(ORIGINAL_SRC/OBJ.name),'receiver_copy_sha256':sha(ROOT/'receiver_copy'/OBJ.name),'byte_identical_receiver_dependency_copies':sourcecopies,'physical_projector_test':False,'MadMapper_playback_test':False,'no_repository_push':True}
    (QA/'Final_Media_QA.json').write_text(json.dumps(qa,indent=2))
    hashes={'READ_ME.txt':sha(ROOT/'READ_ME.txt'),'camera_mapping.npz':sha(ROOT/'camera_mapping.npz')}
    for directory in [OUT,QA,ROOT/'source',ROOT/'receiver_copy']:
        for p in directory.rglob('*'):
            if p.is_file() and p.suffix not in ['.pyc','.blend1'] and p.name not in ['SHA256.json','SHA256SUMS.txt']:
                hashes[str(p.relative_to(ROOT)).replace('\\','/')]=sha(p)
    (ROOT/'SHA256.json').write_text(json.dumps(hashes,indent=2))
    (ROOT/'SHA256SUMS.txt').write_text('\n'.join(f'{h}  {p}' for p,h in hashes.items())+'\n')
    print('ALL FINAL MEDIA CHECKS PASS',flush=True)

if __name__=='__main__':main()
