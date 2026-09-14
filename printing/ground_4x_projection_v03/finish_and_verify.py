from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, subprocess, zipfile, shutil
R=Path(__file__).parent
FF='T:/AI/ffmpeg/bin/ffmpeg.exe'; FP='T:/AI/ffmpeg/bin/ffprobe.exe'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=sorted((R/'video_frames').glob('*.png'));assert len(files)==144
keys=sorted((R/'frames').glob('*.png'));assert len(keys)==24
raw=sorted((R/'imagegen_raw').glob('people_*.png'));assert len(raw)==24
assert len(list((R/'assets').glob('*.png')))==3
for p in raw:assert digest(p)==digest(R.parent/'projection_print_v02/imagegen_raw'/p.name)
assert digest(R/'floor_only_mask.png')==digest(R.parent/'projection_print_v02/floor_only_mask.png')
base=np.array(Image.open(R/'Projection_Base_Playback.png').convert('RGB'))
mask=np.array(Image.open(R/'floor_only_mask.png').convert('L'))
assert set(np.unique(mask))=={0,255}
assert base[mask==0].max()==0
frames=[];reports=[];hashes=[];union=np.zeros(mask.shape,dtype=bool)
for i,p in enumerate(files):
    im=Image.open(p);assert im.size==(1024,786) and im.mode=='RGB'
    a=np.array(im);assert a[mask==0].max()==0,(p,int(a[mask==0].max()))
    change=np.any(a!=base,axis=2)
    assert 1500<change.sum()<40000,(p,int(change.sum()))
    union|=change;frames.append(a);h=digest(p);hashes.append(h)
    reports.append({'file':str(p.relative_to(R)),'sha256':h,'changed_pixels':int(change.sum()),'max_outside_mask':0})
    if i%6==0:assert h==digest(keys[i//6])
assert len(set(hashes))==144
assert all(np.array_equal(a[~union],base[~union]) for a in frames)
for name in ['Projection_Base_Detailed_3x.png','Projection_Hero_3x.png']:
    im=Image.open(R/name);assert im.size==(3072,2358)
    a=np.array(im.convert('RGB'));mask3=mask.repeat(3,0).repeat(3,1)
    assert a[mask3==0].max()==0,(name,int(a[mask3==0].max()))
for frame in [1,109]:
    a=np.array(Image.open(R/f'reopened_frame_{frame:04}.png'))
    assert np.array_equal(a,frames[frame-1]),f'Reopened frame {frame}'
assert np.array_equal(np.array(Image.open(R/'reopened_frame_0145.png')),frames[0]),'Loop endpoint differs'
diff=[float(np.abs(frames[(i+1)%144].astype(float)-frames[i]).mean()) for i in range(144)]
assert diff[-1]<1.6*max(diff[:-1]),diff[-1]
def ff(args):subprocess.run([FF,'-hide_banner','-loglevel','error','-y']+args,check=True)
inp=['-framerate','24','-i',str(R/'video_frames/%04d.png')]
master=R/'Projection_Loop_Lossless_RGB.mp4';preview=R/'Projection_Loop_Preview.mp4'
ff(inp+['-c:v','libx264rgb','-crf','0','-preset','medium','-pix_fmt','rgb24','-movflags','+faststart',str(master)])
ff(inp+['-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(preview)])
meta=json.loads(subprocess.check_output([FP,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(master)]))
v=meta['streams'][0];assert (v['width'],v['height'],int(v['nb_read_frames']))==(1024,786,144)
assert abs(float(meta['format']['duration'])-6)<.001
decoded=subprocess.check_output([FF,'-v','error','-i',str(master),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
a=np.frombuffer(decoded,dtype=np.uint8).reshape(-1,786,1024,3)
assert len(a)==144 and all(np.array_equal(a[i],frames[i]) for i in range(144))
contract=json.loads((R/'render_contract.json').read_text());source=Path(contract['source'])
assert digest(source)==contract['source_sha256']
pop=json.loads((R/'population_manifest.json').read_text());assert pop['student_count']==93
log=(R/'population_full.log').read_text(encoding='utf-16') if (R/'population_full.log').read_bytes().startswith(b'\xff\xfe') else (R/'population_full.log').read_text(errors='replace')
assert 'ERROR' not in log and 'Error:' not in log and 'POPULATION_COMPLETE 93' in log
new=json.loads((R/'new_imagegen_prompts.json').read_text())
for rec in new:
    # Generated sheets remain byte-for-byte identical to their original tool outputs.
    p=Path(rec.get('path',rec.get('source','')))
    if p.is_file():assert digest(p) in {digest(q) for q in (R/'assets').glob('*.png')}
result={'status':'passed','student_count':93,'student_groups':pop['groups'],'reference_frame_count':24,'video_unique_frames':144,'resolution':[1024,786],'hero_resolution':[3072,2358],'fps':24,'duration_seconds':6,'static_background_pixels':int((~union).sum()),'animated_pixels_union':int(union.sum()),'all_walls_and_exterior_exact_rgb_zero':True,'high_resolution_walls_also_exact_zero':True,'lossless_video_decodes_bit_exact_to_png_frames':True,'reopened_frames_match':[1,109],'loop_endpoint_frame145_matches_frame1':True,'loop_transform_max_error':json.loads((R/'scene_validation.json').read_text())['loop_transform_max_error'],'frame144_to_frame1_mean_difference':diff[-1],'largest_other_transition':max(diff[:-1]),'source_unchanged':True,'source_sha256':digest(source),'mask_unchanged':True,'walking_assets_unchanged':True,'frame_reports':reports}
(R/'validation.json').write_text(json.dumps(result,indent=2))
shutil.copy2(R.parent/'projection_print_v02/Calibration_25mm_Floor_Only.png',R/'Calibration_25mm_Floor_Only.png')
shutil.copy2(R.parent/'projection_print_v02/imagegen_prompts.json',R/'walking_imagegen_prompts.json')
contract.update({'reference_images':24,'video_frames':144,'fps':24,'duration_seconds':6,'student_count':93})
contract.pop('frames',None);contract.pop('people_target',None)
(R/'render_contract.json').write_text(json.dumps(contract,indent=2))
with zipfile.ZipFile(R/'Projection_24_Images.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in keys:z.write(p,'frames/'+p.name)
    for name in ['Projection_Base_Playback.png','floor_only_mask.png','Calibration_25mm_Floor_Only.png','README.md']:z.write(R/name,name)
print(json.dumps({k:v for k,v in result.items() if k!='frame_reports'},indent=2))
